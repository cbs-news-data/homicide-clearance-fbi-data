"""downloads supplementary homicide report documents from 1995-present to raw"""

import os
import subprocess
from remotezip import RemoteZip
import requests
from tqdm import tqdm

BASE_URL = "https://s3-us-gov-west-1.amazonaws.com/cg-d4b776d0-d898-4153-90c8-8336f86bdfec/masters"

FILES = ["reta", "shr", "nibrs"]

for year in tqdm(range(1995, 2021), desc="Download files", leave=False):
    for fbi_file in FILES:
        # all urls use the same format
        url = f"{BASE_URL}/{fbi_file}/{fbi_file}-{year}.zip"
        dirname = f"raw/{fbi_file}"
        # the zipfile module only supports CRC32-encrypted zip files, but some older FBI files
        # use other, unsupported encryption methods. Attempt to unzip the files with default
        # encryption, then use 7zip if that fails
        ATTEMPTS = 0
        while ATTEMPTS < 3:
            try:
                with RemoteZip(url) as remote_zip:
                    for zipped_file in remote_zip.infolist():
                        if not os.path.exists(f"{dirname}/{zipped_file.filename}"):
                            remote_zip.extract(zipped_file, dirname)

            except NotImplementedError as exc:
                ATTEMPTS += 1
                print(f"reading zip file from remote failed. retrying {ATTEMPTS}/3")

            else:
                break

        else:
            print("reading zip file from remote url failed. retrying with 7zip.")

            resp = requests.get(url)
            if resp.status_code != 200:
                raise ValueError(f"request returned status code {resp.status_code}")

            try:
                TEMP_FILENAME = "response-temp.zip"
                with open(TEMP_FILENAME, "wb") as zip_file:
                    zip_file.write(resp.content)

                subprocess.call(
                    [
                        "7z",
                        "x",
                        "-ppassword",
                        f"-o{dirname}",
                        TEMP_FILENAME,
                    ]
                )

            finally:
                if os.path.exists(TEMP_FILENAME):
                    os.remove(TEMP_FILENAME)
