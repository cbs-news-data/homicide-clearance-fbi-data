"""handles custom commands for loading csv data to django"""

import csv
from itertools import islice
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models.fields.related import ForeignKey
from tqdm import tqdm
from data import models
from .utils import guess_n_loops


def bulk_create(lines, model, preprocessors=None, fk_pk_field=None, fk_model=None):
    """gets a list of models based on lines of a csv.DictReader and runs bulk_create

    Args:
        lines (list): list of dicts from csv.DictReader
        model (django.db.models.Model): type of model to create
        preprocessors (dict, optional): Dictionary of field names and functions to
            apply before creating models. Defaults to None.
        fk_pk_field (str, optional): name of field containing a foreign key.
            Defaults to None.
        fk_model (django.db.models.Model, optional): model class to use as foreign key.
            Defaults to None.

    Raises:
        ValueError: if both fk_pk_field and fk_model are not provided together
    """
    if preprocessors is None:
        preprocessors = {}

    foreign_args = [arg is not None for arg in [fk_pk_field, fk_model]]
    if any(foreign_args) and not all(foreign_args):
        raise ValueError("you must provide both fk_pk_field and fk_model")

    dict_data = []
    for row_dict in lines:
        for field in preprocessors:
            if field in row_dict:
                row_dict[field] = preprocessors[field](row_dict[field])

        if fk_pk_field is not None:
            # get the name of the foreign key for model
            fields = model._meta.get_fields()
            fk_fields = []
            for field in fields:
                if isinstance(field, ForeignKey):
                    fk_fields.append(field)

            if len(fk_fields) == 0:
                raise ValueError(
                    f"model '{model}' has no foreign key but one was passed"
                )
            elif len(fk_fields) > 1:
                raise NotImplementedError(
                    f"model '{model}' has multiple foreign keys, which is not supported"
                )
            else:
                fk_field = fk_fields[0]

            foreign_obj = fk_model.objects.get(pk=row_dict[fk_pk_field])
            row_dict[fk_field.name] = foreign_obj
            del row_dict[fk_pk_field]

        dict_data.append(row_dict)

    objs = [model(**d) for d in dict_data]
    model.objects.bulk_create(objs)


def int_if_not_empty(val):
    if str(val) == "":
        return None

    return int(float(val))


def load_shr_incidents(lines):
    preprocessors = {
        "year": int_if_not_empty,
        "last_update": lambda val: None if val == "" else val,
    }
    bulk_create(lines, models.SHRIncidents, preprocessors)


def load_shr_offenders(lines):
    preprocessors = {
        "offender_age": int_if_not_empty,
    }
    bulk_create(
        lines,
        models.SHROffenders,
        preprocessors=preprocessors,
        fk_pk_field="incident_unique_id",
        fk_model=models.SHRIncidents,
    )


def load_shr_victims(lines):
    preprocessors = {
        "victim_age": int_if_not_empty,
        "year": int_if_not_empty,
    }
    bulk_create(
        lines,
        models.SHRVictims,
        preprocessors=preprocessors,
        fk_pk_field="incident_unique_id",
        fk_model=models.SHRIncidents,
    )


# RUN IN THIS ORDER
LOADERS = {
    "input/shr_incidents.csv": load_shr_incidents,
    "input/shr_offenders.csv": load_shr_offenders,
    "input/shr_victims.csv": load_shr_victims,
    "input/agencies.csv": lambda lines: bulk_create(lines, models.Agencies),
    "input/reta_master.csv": lambda lines: bulk_create(lines, models.RetA),
}


class Command(BaseCommand):
    """loads data from csv to database"""

    def handle(self, *args, **options):
        for filename, loader in LOADERS.items():
            with open(filename, "r", encoding="UTF-8") as csv_file:
                reader = csv.DictReader(csv_file)

                for lines in tqdm(
                    iter(
                        lambda reader=reader: tuple(islice(reader, settings.CHUNKSIZE)),
                        (),
                    ),
                    desc=f"load {filename}",
                    total=guess_n_loops(filename, settings.CHUNKSIZE),
                    leave=True,
                ):
                    loader(lines)
