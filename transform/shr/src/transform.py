"""transforms the output of fixed width file extraction"""

import logging
import sys
import pandas as pd
from standardize import standardize_ori
from assign_unique_ids import assign_unique_ids

logging.basicConfig(filename="output/transform.log", filemode="w", level=logging.INFO)

# columns that begin with the word "offender" or "victim" but do not contain offender information
EXCLUDE_COLS = ["victim_count", "offender_count"]


def drop_empty_rows(df):
    """drops completely empty rows"""
    orig_len = len(df)
    # drop if the only non-empty value is the id
    df = df.dropna(how="all", subset=[c for c in df.columns if c != "shr_id"]).copy()
    dropped_rows = orig_len - len(df)
    if dropped_rows > 0:
        logging.info("Dropped %s blank rows", dropped_rows)
    return df


def clean_year(yearno):
    """converts years in original format to full 4-digit years"""
    if pd.isna(yearno):
        return yearno

    # data starts at 1965
    if yearno >= 65:
        return yearno + 1900

    return yearno + 2000


def clean_update_date(update_date):
    """converts original variable-length mdy format to pandas Timestamp"""
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
                rf"(?<={fieldname})\d*(?=_)", "", regex=True
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
        "output/shr_incidents.csv": df[
            [
                "incident_unique_id",
                "ori_code",
                "last_update",
                "year",
                "homicide",
                "situation",
            ]
        ],
        "output/shr_offenders.csv": split_records(df, "offender"),
        "output/shr_victims.csv": split_records(df, "victim"),
    }
    for filename, out_df in out_dfs.items():
        out_df.to_csv(filename, index=False)


if __name__ == "__main__":
    do_transformation(pd.read_csv(sys.argv[1], low_memory=False))
