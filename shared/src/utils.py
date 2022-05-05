"""contains utility functions used across two or more python modules"""

import math


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
