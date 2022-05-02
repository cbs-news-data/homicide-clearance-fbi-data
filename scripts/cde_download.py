"""downloads supplementary homicide report documents from 1985-present to raw"""

import os
from remotezip import RemoteZip
from tqdm import tqdm

BASE_URL = "https://s3-us-gov-west-1.amazonaws.com/cg-d4b776d0-d898-4153-90c8-8336f86bdfec/masters"

FILES = ["shr", "nibrs"]

for year in tqdm(range(1995, 2021), desc="Download files", leave=False):
    for fbi_file in FILES:
        url = f"{BASE_URL}/{fbi_file}/{fbi_file}-{year}.zip"
        with RemoteZip(url) as remote_zip:
            for zipped_file in remote_zip.infolist():
                dirname = f"raw/{fbi_file}"
                if not os.path.exists(f"{dirname}/{zipped_file.filename}"):
                    remote_zip.extract(zipped_file, dirname)
