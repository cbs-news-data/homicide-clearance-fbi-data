"""downloads supplementary homicide report documents from 1985-present to raw/"""

from io import BytesIO
import zipfile
import requests
from tqdm import tqdm

BASE_URL = (
    "https://s3-us-gov-west-1.amazonaws.com/cg-d4b776d0-d898-4153-90c8-8336f86bdfec/"
    "masters/shr"
)

for year in tqdm(range(1985, 2021), desc="Download files", leave=False):
    url = f"{BASE_URL}/shr-{year}.zip"
    resp = requests.get(url)

    if not resp.status_code == 200:
        raise ValueError(f"Request returned code {resp.status_code}, expected 200")

    with zipfile.ZipFile(BytesIO(resp.content)) as zip_file:
        zip_file.extractall("raw/shr")
