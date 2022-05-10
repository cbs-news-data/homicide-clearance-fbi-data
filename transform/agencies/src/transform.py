"""makes transformations on agency data"""

import logging
import sys
import pandas as pd
from standardize import standardize_ori
from assign_unique_ids import assign_unique_ids

logging.basicConfig(filename="output/transform.log", filemode="w", level=logging.INFO)


def do_transform(dataframe):
    """does all necessary transformations"""

    dataframe["ori"] = dataframe.ori.apply(standardize_ori)
    dataframe = assign_unique_ids(dataframe, "data_year", "ori")
    return dataframe


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1], low_memory=False)
    df = do_transform(df)
    print(df.to_csv(index=False, line_terminator="\n"))
    logging.info(
        "wrote %s lines and %s columns to file.",
        len(df),
        len(df.columns),
    )
