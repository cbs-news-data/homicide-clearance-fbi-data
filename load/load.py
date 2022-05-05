"""uses pandas to load csv data from previous tasks to django orm"""

import argparse
import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings
import pandas as pd
from tqdm import tqdm
from data import models

parser = argparse.ArgumentParser()
parser.add_argument("csv_files", nargs="+")
args = parser.parse_args()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
application = get_wsgi_application()

for filename in tqdm(args.csv_files, desc="csv files"):
    try:
        model_name = settings.CSV_FILES[os.path.basename(filename)]
    except KeyError as exc:
        raise ValueError(
            f"file '{filename}' does not have an associated model defined in settings.CSV_FILES"
        ) from exc

    try:
        model = models.__dict__[model_name]
    except KeyError as exc:
        raise ValueError(
            f"model '{model_name}' does not exist in models/__init__.py"
        ) from exc

    chunks = pd.read_csv(filename, chunksize=settings.CHUNKSIZE, low_memory=False)
    for chunk in tqdm(chunks, desc="batch process large file", leave=False):
        for _, row in tqdm(chunk.iterrows(), desc="rows", leave=False):
            kwargs = {}
            for field in model._meta.get_fields():  # pylint: disable=protected-access
                field = field.name
                try:
                    kwargs[field] = row[field]
                except KeyError as exc:
                    raise ValueError(
                        f"file '{filename}' is missing required field '{field}'"
                    ) from exc
            _, created = model.objects.update_or_create(**kwargs)
