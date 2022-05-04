"""
transforms the output of in2csv's parsing of the fixed-width files to more usable formats
"""

import logging
import math
import re
import sys
import pandas as pd
from tqdm import tqdm
import yaml

# regex pattern to match all total columns I actually care about
TOTAL_COLS_PAT = r"^[a-z]{3}_(actual|cleared_arrest)_(?![A-Z]+)"

OTHER_COLS_PATS = [
    # data I'll use in cleaning tasks
    "info_month_included_in",
]

# other columns I want to be the index of the output file
INDEX_COLS = [
    # agency and report data
    "ori_code",
    "agency_name",
    "agency_state_name",
    "year",
]

KEEP_COLS_PATS = [TOTAL_COLS_PAT] + INDEX_COLS + OTHER_COLS_PATS


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


def replace_vals_from_yaml(df, yaml_filename):
    """replaces the values of a column in df with the values named in a yaml file

    Args:
        df (pandas.DataFrame): dataframe to replace
        yaml_filename (str):
            path to yaml file containing values and their replacements.
            the filename must be the the name of a column in df

    Raises:
        ValueError: if the filename couldn't be parsed
        ValueError: if the filename is not a column in the dataframe
        ValueError: if the yaml file isn't read as a dictionary

    Returns:
        pandas.DataFrame: dataframe with values replaced
    """
    # ensure the file name is a column in df
    match = re.search(
        r"^(?P<path>.*\/)?(?P<filename>[^\/]+?|)(?=(?:\.[^\/.]*)?$)",
        yaml_filename,
    )
    if match is None:
        raise ValueError(f"failed to extract filename from path '{yaml_filename}'")

    # name of the file must be the name of a column in df
    colname = match.group("filename")
    if colname not in df.columns:
        raise ValueError(
            f"the name of file '{yaml_filename}' must be the name of a column in the data. "
            f"Columns are: {', '.join(df.columns.tolist())}"
        )

    # must be a mapping of values and their replacements
    with open(yaml_filename, "r", encoding="UTF-8") as yaml_file:
        replace_vals = yaml.load(yaml_file, Loader=yaml.CLoader)
        if not isinstance(replace_vals, dict):
            raise ValueError(
                f"malformed yaml file. must be a dictionary, got {type(replace_vals)}"
            )

    df = df.replace({colname: replace_vals})

    return df


if __name__ == "__main__":
    logging.basicConfig(
        filename="output/transform.log", filemode="w", level=logging.INFO
    )

    CHUNKSIZE = 1000  # using a small chunksize as the resulting files are 600x taller
    ENCODING = "latin1"

    # guess how many itereations are required for the progress bar and logging
    with open(sys.argv[1], encoding=ENCODING) as file:
        total_loops = math.ceil(sum(1 for _ in file) / CHUNKSIZE)

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

        # drop the columns you don't want
        chunk = chunk[KEEP_COLS]

        # melt the dataframe
        chunk = melt_df(chunk, KEEP_COLS)

        # split the 'variable' column and reorder columns
        chunk = split_variable(chunk)

        # replace values from yaml files in hand/
        for filename in sys.argv[2:-1]:
            assert filename.endswith(".yaml") or filename.endswith(".yml"), (
                "all other arguments besides input file must be yaml files, except for "
                "last argument, which should be output file"
            )
            chunk = replace_vals_from_yaml(chunk, filename)

        if loop_index == 0:
            MODE = "w"
            HEADER = True
        else:
            MODE = "a"
            HEADER = False

        chunk.to_csv(sys.argv[-1], index=False, mode=MODE, header=HEADER)

        logging.info(
            "[%s/%s] wrote %s lines to file.",
            loop_index + 1,
            total_loops,
            len(chunk),
        )