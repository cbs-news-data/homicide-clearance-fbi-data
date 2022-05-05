"""downloads supplementary homicide report documents from 1995-present to raw"""

import os
import subprocess
from remotezip import RemoteZip
import requests
from tqdm import tqdm

BASE_URL = (
    "https://s3-us-gov-west-1.amazonaws.com/cg-d4b776d0-d898-4153-90c8-8336f86bdfec"
)

FILES = ["reta", "shr", "nibrs"]


def download_zip(url, dirname):
    """downloads and extracts all files in zip file at url to dirname"""
    # the zipfile module only supports CRC32-encrypted zip files, but some older FBI files
    # use other, unsupported encryption methods. Attempt to unzip the files with default
    # encryption, then use 7zip if that fails
    attempts = 0
    while attempts < 3:
        try:
            with RemoteZip(url) as remote_zip:
                for zipped_file in remote_zip.infolist():
                    if not os.path.exists(f"{dirname}/{zipped_file.filename}"):
                        remote_zip.extract(zipped_file, dirname)

        except NotImplementedError:
            attempts += 1
            print(f"reading zip file from remote failed. retrying {attempts}/3")

        else:
            break

    else:
        print("reading zip file from remote url failed. retrying with 7zip.")

        resp = requests.get(url)
        if resp.status_code != 200:
            raise ValueError(f"request returned status code {resp.status_code}")

        try:
            temp_filename = "response-temp.zip"
            with open(temp_filename, "wb") as zip_file:
                zip_file.write(resp.content)

            subprocess.call(
                [
                    "7z",
                    "x",
                    "-ppassword",
                    f"-o{dirname}",
                    temp_filename,
                ]
            )

        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)


if __name__ == "__main__":
    # download masters
    for year in tqdm(range(1995, 2021), desc="Download files", leave=False):
        for fbi_file in FILES:
            # all urls use the same format
            file_url = f"{BASE_URL}/masters/{fbi_file}/{fbi_file}-{year}.zip"
            file_dirname = f"raw/{fbi_file}"

            download_zip(file_url, file_dirname)

    # download agencies
    download_zip(f"{BASE_URL}/agencies.zip", "raw/agencies")
