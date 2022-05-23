"""contains utility functions used across two or more python modules"""

import re
import math
import yaml


def guess_n_loops(filename, chunksize, encoding="utf-8"):
    """calculates the number of iterations to process a file

    Args:
        filename (str): name of file
        chunksize (int): number of rows per process
        encoding (str, optional): encoding of file. Defaults to "utf-8".

    Returns:
        int: number of iterations needed
    """
    with open(filename, "r", encoding=encoding) as file:
        total_loops = math.ceil(sum(1 for _ in file) / chunksize)
    return total_loops


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
