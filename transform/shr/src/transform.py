"""transforms the output of fixed width file extraction"""

import logging
import sys
import numpy as np
import pandas as pd
from standardize import standardize_ori
from assign_unique_ids import assign_unique_ids

logging.basicConfig(filename="output/transform.log", filemode="w", level=logging.INFO)

# columns that begin with the word "offender" or "victim" but do not contain offender information
EXCLUDE_COLS = ["victim_count", "offender_count"]

# see documents/ucr-2019-NIBRS-technical-specification-070120.pdf page 103
AGE_VALUES = {
    "NN": 0,
    "NB": 0,
    "BB": 0,
    "00": np.NaN,  # used to define 'unknown'
}

# dtypes that need to be changed
DTYPES = {
    "incidents": {"year": float},
    "offenders": {
        "year": int,
        "offender_age": float,
    },
}


def drop_empty_rows(df):
    """drops completely empty rows

    Args:
        df (pandas.DataFrame): dataframe to drop from

    Returns:
        pandas.DataFrame: dataframe with rows removed
    """
    orig_len = len(df)
    # drop if the only non-empty value is the id
    df = df.dropna(how="all", subset=[c for c in df.columns if c != "id"]).copy()
    dropped_rows = orig_len - len(df)
    if dropped_rows > 0:
        logging.info("Dropped %s blank rows", dropped_rows)
    return df


def clean_year(yearno):
    """converts years in original format to full 4-digit years

    Args:
        yearno (any): existing year value

    Returns:
        int | np.NaN: integer or NaN if provided value was NaN
    """
    if pd.isna(yearno):
        return yearno

    # data starts at 1965
    if yearno >= 65:
        return yearno + 1900

    return yearno + 2000


def clean_age(age):
    """cleans offender age values

    Args:
        age (any): existing age value

    Returns:
        int | np.NaN: integer or NaN if invalid age
    """

    try:
        age = str(int(age)).zfill(2)
    except ValueError as exc:
        ermsg = str(exc)
        if ermsg == "cannot convert float NaN to integer":
            return np.NaN
        # if a string, hold on to the value and try converting it from known string values
        if not ermsg.startswith("invalid literal for int() with base 10:"):
            raise exc

    if age in AGE_VALUES:
        return AGE_VALUES[age]

    if age.isnumeric():
        return float(age)

    raise ValueError(ermsg)


def clean_update_date(update_date):
    """converts original variable-length mdy format to pandas Timestamp

    Args:
        update_date (float): original date value

    Returns:
        pd.Timestamp: parsed date value
    """
    if pd.isna(update_date):
        return update_date

    update_date = str(int(update_date))
    assert len(update_date) in [5, 6], update_date
    update_date = str(int(update_date)).zfill(6)

    update_date = pd.to_datetime(update_date, format="%m%d%y")
    return update_date


def split_records(df, fieldname):
    """splits rows describing multiple people to one row per individual"""
    field_df = (
        df.melt(
            id_vars=["incident_unique_id", "ori_code", "year"],
            value_vars=[
                col
                for col in df.columns
                if col.startswith(fieldname) and col not in EXCLUDE_COLS
            ],
        )
        .query("value.notna()")
        .reset_index()
        .pipe(assign_unique_ids, "index")
        .rename(columns={"unique_id": f"{fieldname}_unique_id"})
        .drop("index", axis=1)
        .assign(
            **{
                f"{fieldname}_sequence": lambda df: df.variable.str.extract(
                    rf"(?<={fieldname})(?P<seq>\d*)(?=_)"
                )["seq"]
                .replace({"": 0})
                .astype(int)
                .add(1)  # from 0-indexed to 1
            }
        )
        .assign(
            variable=lambda df: df.variable.str.replace(
                # strip group numbers from variable names
                # e.g. "victim2_age -> victim_age"
                rf"(?<={fieldname})\d*(?=_)",
                "",
                regex=True,
            )
        )
        .pivot(
            index=[
                f"{fieldname}_unique_id",
                "incident_unique_id",
                "year",
                "ori_code",
                f"{fieldname}_sequence",
            ],
            columns="variable",
            values="value",
        )
        .reset_index()
    )
    logging.info("Extracted %s %s records", len(field_df), fieldname)
    return field_df


def do_transformation(df):
    """does all necessary transformations"""
    # first drop all empty rows
    df = drop_empty_rows(df)
    # then do initial cleaning and standardization
    df["year"] = df.year.apply(clean_year)
    df["last_update"] = df.last_update.apply(clean_update_date)
    df["ori_code"] = df.ori_code.apply(standardize_ori)
    # assign unique IDs
    # using index becasue each row should be unique
    df = (
        assign_unique_ids(df.reset_index(), "index")
        .rename(
            # rename uid field
            columns={"unique_id": "incident_unique_id"}
        )
        .drop("index", axis=1)
    )

    # output victims, offenders and case information separately
    out_dfs = {
        "incidents": df[
            [
                "incident_unique_id",
                "ori_code",
                "last_update",
                "year",
                "homicide",
                "situation",
            ]
        ],
        "offenders": split_records(df, "offender"),
        "victims": split_records(df, "victim"),
    }
    for filename, out_df in out_dfs.items():
        try:
            # cleaners that need to be applied to each individual dataframe post-transformation
            age_fields = ["victim", "offender"]
            for age_field in age_fields:
                age_field = f"{age_field}_age"
                if age_field in out_df.columns:
                    out_df[age_field] = out_df[age_field].apply(clean_age)

            # change necessary dtypes
            if filename in DTYPES:
                out_df = out_df.astype(DTYPES[filename])

            out_df.to_csv(f"output/shr_{filename}.csv", index=False)

        except Exception as exc:
            raise ValueError(
                f"An error occurred while cleaning '{filename}' data."
            ) from exc


if __name__ == "__main__":
    do_transformation(pd.read_csv(sys.argv[1], low_memory=False))
