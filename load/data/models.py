"""contains database models"""

from django.db import models


class RetA(models.Model):
    """handles cleaned return A data"""

    ori_code = models.CharField(max_length=7)
    agency_name = models.CharField(max_length=25)
    core_city = models.BooleanField()
    agency_state_name = models.CharField(max_length=6)
    year = models.IntegerField()
    month = models.CharField(max_length=3)
    card = models.CharField(max_length=14)
    category = models.CharField(max_length=255)
    value = models.IntegerField()


class Agencies(models.Model):
    """handles cleaned agency data"""

    data_year = models.IntegerField(choices=[(i, i) for i in range(1960, 2021)])
    ori = models.CharField(max_length=50)
    ncic_agency_name = models.CharField(max_length=50)
    state_abbr = models.CharField(max_length=2)
    population = models.IntegerField
    county_name = models.CharField(max_length=50)
    msa_name = models.CharField(max_length=50)
