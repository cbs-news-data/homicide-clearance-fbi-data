"""extracts unique ORIs and city names from reta data"""

import sys
import pandas as pd
from tqdm import tqdm
from standardize import standardize_ori
from utils import guess_n_loops

CHUNKSIZE = 10000
ENCODING = "latin1"
SELECT_COLUMNS = ["ori_code", "mailing_addr_line4"]
COLNAME = "city_name"

chunks = pd.read_csv(
    sys.argv[1],
    chunksize=CHUNKSIZE,
    encoding=ENCODING,
    low_memory=False,
)

dfs = []

for i, chunk in tqdm(
    enumerate(chunks),
    total=guess_n_loops(sys.argv[1], chunksize=CHUNKSIZE, encoding=ENCODING),
):
    chunk = chunk[SELECT_COLUMNS].copy()
    chunk[COLNAME] = chunk.mailing_addr_line4.str.extract(rf"^(?P<{COLNAME}>.*)(?=,)")[
        COLNAME
    ]
    del chunk["mailing_addr_line4"]
    chunk = chunk.dropna(subset=COLNAME)
    chunk["ori_code"] = chunk.ori_code.apply(standardize_ori)
    dfs.append(chunk)

print(
    pd.concat(dfs)
    .drop_duplicates(subset="ori_code", keep="first")
    .to_csv(index=False, line_terminator="\n")
)
