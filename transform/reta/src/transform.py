"""
transforms the output of in2csv's parsing of the fixed-width files to more usable formats
"""

import logging
import re
import sys
import numpy as np
import pandas as pd
from tqdm import tqdm
from utils import guess_n_loops, replace_vals_from_yaml
from standardize import standardize_ori
from assign_unique_ids import assign_unique_ids

logging.basicConfig(filename="output/transform.log", filemode="w", level=logging.INFO)

# regex pattern to match all total columns I actually care about
TOTAL_COLS_PAT = r"^[a-z]{3}_(actual|cleared_arrest)_(murder)"

OTHER_COLS_PATS = [
    # data I'll use in cleaning tasks
    "info_month_included_in",
]

# other columns I want to be the index of the output file
INDEX_COLS = [
    # agency and report data
    "ori_code",
    "agency_name",
    "core_city",
    "agency_state_name",
    "year",
]

KEEP_COLS_PATS = [TOTAL_COLS_PAT] + INDEX_COLS + OTHER_COLS_PATS

DTYPES = {
    "ori_code": str,
    "agency_name": str,
    "core_city": bool,
    "agency_state_name": str,
    "year": int,
    "month": str,
    "card": str,
    "category": str,
    "value": int,
}

# list of dictionaries mapping column names to values for rows I want dropped
DROP_ROWS = [
    {
        "ori_code": "OH0720300",
        "agency_name": "FREMONT",
        "card": "cleared_arrest",
        "year": 2017,
    }
]


def select_columns(df):
    """
    selects only the  needed columns in the data based on the regex patterns
    defined as constants in this module. There is a lot of data in here that I don't need,
    and this reduces the memory load of clearning the data significantly.

    Args:
        df (pandas.DataFrame): dataframe to select columns from

    Raises:
        ValueError: if any pattern in KEEP_COLS_PATS matches 0 columns in df

    Returns:
        list: list of column names to keep
    """
    keep_cols = []
    # check that all column patterns match at least 1 pattern
    for pat in KEEP_COLS_PATS:
        matches = 0
        for col in df.columns:
            # don't re-check if already matched
            if col not in keep_cols:
                match = re.search(pat, col)
                if match is not None:
                    keep_cols.append(col)
                    matches += 1
        if matches == 0:
            raise ValueError(f"pattern '{pat}' matched 0 columns")

    return keep_cols


def melt_df(df, cols):
    """turns specified cols in df to rows

    Args:
        df (pandas.DataFrame): dataframe to melt
        cols (list): list of column names

    Returns:
        pandas.DataFrame: melted dataframe
    """
    return df.melt(
        id_vars=INDEX_COLS,
        value_vars=[col for col in cols if re.search(TOTAL_COLS_PAT, col) is not None],
    )


def split_variable(df):
    """splits the 'variable' column into multiple columns based on regex

    Args:
        df (pandas.DataFrame): dataframe containing a column named 'variable'

    Returns:
        pandas.DataFrame: dataframe with variable column split into multiple columns
    """
    # get a dataframe with matches of regex
    extract_df = df.variable.str.extract(
        r"^(?P<month>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)_"
        r"(?P<card>actual|cleared_arrest)_(?P<category>[a-z\d_]*?$)"
    )
    # store group names for later
    group_names = extract_df.columns.tolist()
    # join the dataframes
    df = df.join(extract_df)
    # conserve memory
    del extract_df

    # reorder columns
    drop_cols = ["variable"]
    df = df[[col for col in df.columns if col not in drop_cols]]
    df = df.set_index(INDEX_COLS + group_names).reset_index()

    return df


def drop_unrecognized_negative_value_entries(df):
    """
    drops any remaining non-numeric values after attempting conversion.
    some values contain negative entries that are not documented, so they must be dropped.

    Args:
        df (pandas.DataFrame): dataframe to drop from

    Returns:
        pandas.DataFrame: dataframe with entries dropped
    """

    def try_convert(val):
        try:
            float(val)
        except ValueError:
            return np.NaN
        else:
            return val

    df["value"] = df.value.apply(try_convert)
    return df


def coerce_dtype(df):
    """sets the dtypes of each column defined in the DTYPES constant at the top of this module

    Args:
        df (pandas.DataFrame): dataframe to coerce

    Returns:
        pandas.DataFrame: dataframe with dtypes fixed
    """
    return df.astype(DTYPES)


def drop_blank_rows(df):
    """drops all rows that are missing all index values

    Args:
        df (pandas.DataFrame): dataframe to drop from

    Returns:
        pandas.DataFrame: dataframe with missing data dropped
    """
    orig_len = len(df)
    df = df.dropna(axis=0, how="all", subset=INDEX_COLS)
    n_dropped = orig_len - len(df)
    if n_dropped > 0:
        logging.info("dropped %s rows with missing index values", orig_len - len(df))
    return df


def drop_duplicate_rows(df):
    """drops entirely duplicate rows"""
    orig_len = len(df)
    df = df.drop_duplicates(keep="first")
    new_len = len(df)
    n_dropped = orig_len - new_len
    if n_dropped > 0:
        logging.info("dropped %s rows with missing index values", orig_len - new_len)
    return df


def manual_drop_rows(df):
    """Drops rows described in DROP_ROWS"""

    for row_dict in DROP_ROWS:
        df = df.loc[~(df[row_dict.keys()].isin(row_dict.values()).all(axis=1))]

    return df


def do_transformation(df):
    """does all necessary transformations on the data

    Args:
        df (pandas.DataFrame): original dataframe from the output of extract/

    Returns:
        pandas.DataFrame: transformed dataframe
    """
    # drop rows missing all index data (there are a few)
    df = drop_blank_rows(df)
    # drop the columns you don't want
    df = df[KEEP_COLS]
    # melt the dataframe
    df = melt_df(df, KEEP_COLS)
    # replace values from yaml files in hand/
    for filename in sys.argv[2:-1]:
        assert filename.endswith(".yaml") or filename.endswith(".yml"), (
            "all other arguments besides input file must be yaml files, except for "
            "last argument, which should be output file"
        )
        df = replace_vals_from_yaml(df, filename)
    # drop any negative value entries that weren't replaced
    df = drop_unrecognized_negative_value_entries(df)
    # split the 'variable' column and reorder columns
    df = split_variable(df)
    # fill all NaN values with 0
    df["value"] = df.value.fillna(0)
    # coerce dtypes
    df = coerce_dtype(df)
    # standardization
    df["ori_code"] = df.ori_code.apply(standardize_ori)
    # drop duplicates on all rows
    df = drop_duplicate_rows(df)
    # assign unique IDs
    df = assign_unique_ids(
        df,
        "year",
        "month",
        "ori_code",
        "agency_name",
        "card",
        "category",
    )
    df = manual_drop_rows(df)
    return df


if __name__ == "__main__":
    CHUNKSIZE = 1000  # using a small chunksize as the resulting files are 600x taller
    ENCODING = "latin1"

    total_loops = guess_n_loops(sys.argv[1], CHUNKSIZE, ENCODING)

    chunks = pd.read_csv(
        sys.argv[1],
        chunksize=CHUNKSIZE,
        encoding=ENCODING,
        low_memory=False,
        dtype={
            "year": str,  # it's a 2-digit code representing the last 2 digits of the year
        },
    )

    KEEP_COLS = None
    for loop_index, chunk in tqdm(
        enumerate(chunks),
        desc="transform file",
        total=total_loops,
        leave=False,
    ):
        if KEEP_COLS is None:
            KEEP_COLS = select_columns(chunk)

        chunk = do_transformation(chunk)

        if loop_index == 0:
            MODE = "w"
            HEADER = True
        else:
            MODE = "a"
            HEADER = False

        chunk.to_csv(sys.argv[-1], index=False, mode=MODE, header=HEADER)

        logging.info(
            "[%s/%s] wrote %s lines and %s columns to file.",
            loop_index + 1,
            total_loops,
            len(chunk),
            len(chunk.columns),
        )
