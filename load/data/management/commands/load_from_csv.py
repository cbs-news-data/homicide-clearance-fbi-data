"""handles custom commands for loading csv data to django"""

import csv
from itertools import islice
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from tqdm import tqdm
from data import models
from .utils import guess_n_loops


class Command(BaseCommand):
    """loads data from csv to database"""

    def add_arguments(self, parser):
        parser.add_argument("csv_files", nargs="+", type=str)

    def handle(self, *args, **options):
        for filename in tqdm(options["csv_files"], desc="csv files"):
            try:
                model_name = settings.CSV_FILES[os.path.basename(filename)]
            except KeyError as exc:
                raise ValueError(
                    f"file '{filename}' does not have an associated model "
                    "defined in settings.CSV_FILES"
                ) from exc

            try:
                model = models.__dict__[model_name]
            except KeyError as exc:
                raise ValueError(
                    f"model '{model_name}' does not exist in models/__init__.py"
                ) from exc

            model_fields = [
                field.name
                for field in model._meta.get_fields()  # pylint: disable=protected-access
                if field.name != "id"
            ]

            with open(filename, "r", encoding="UTF-8") as csv_file:
                reader = csv.DictReader(csv_file)

                for lines in tqdm(
                    iter(
                        lambda reader=reader: tuple(islice(reader, settings.CHUNKSIZE)),
                        (),
                    ),
                    desc="batch process file",
                    total=guess_n_loops(filename, settings.CHUNKSIZE),
                    leave=False,
                ):
                    objs = [
                        model(**{field: row[field] for field in model_fields})
                        for row in lines
                    ]

                    model.objects.bulk_create(objs)
