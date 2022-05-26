"""contains database models"""

from django.db import models
from .validators import validate_ori


class RetA(models.Model):
    """handles cleaned return A data"""

    unique_id = models.CharField(max_length=40, unique=True, primary_key=True)
    ori_code = models.CharField(max_length=9, validators=[validate_ori])
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

    unique_id = models.CharField(max_length=40, unique=True, primary_key=True)
    data_year = models.IntegerField(choices=[(i, i) for i in range(1960, 2021)])
    ori = models.CharField(max_length=9, validators=[validate_ori])
    ncic_agency_name = models.CharField(max_length=50)
    state_abbr = models.CharField(max_length=2)
    population = models.IntegerField
    county_name = models.CharField(max_length=50)
    msa_name = models.CharField(max_length=50)
    city_name = models.CharField(max_length=50)


class SHRIncidents(models.Model):
    """handles cleaned SHR Incident data"""

    incident_unique_id = models.CharField(max_length=40, unique=True, primary_key=True)
    ori_code = models.CharField(max_length=9, validators=[validate_ori])
    last_update = models.DateField()
    year = models.IntegerField(null=True)
    homicide = models.CharField(max_length=1)
    situation = models.CharField(max_length=1)


class SHROffenders(models.Model):
    """handles cleaned SHR Offender data"""

    offender_unique_id = models.CharField(max_length=40, unique=True, primary_key=True)
    incident = models.ForeignKey(to=SHRIncidents, on_delete=models.CASCADE)
    year = models.IntegerField()
    ori_code = models.CharField(max_length=9, validators=[validate_ori])
    offender_sequence = models.IntegerField(choices=[(i, i) for i in range(1, 13)])
    offender_age = models.IntegerField(blank=True, null=True)
    offender_circumstance = models.CharField(max_length=10)
    offender_ethnicity = models.CharField(max_length=10)
    offender_race = models.CharField(max_length=10)
    offender_relationship = models.CharField(max_length=10)
    offender_sex = models.CharField(max_length=10)
    offender_subcircumstance = models.CharField(max_length=10)
    offender_weapon = models.CharField(max_length=10)
    offender_weapon_used = models.CharField(max_length=10)


class SHRVictims(models.Model):
    """handles cleaned SHR Victim data"""

    victim_unique_id = incident_unique_id = models.CharField(
        max_length=40, unique=True, primary_key=True
    )
    incident = models.ForeignKey(to=SHRIncidents, on_delete=models.CASCADE)
    year = models.IntegerField()
    ori_code = models.CharField(max_length=9, validators=[validate_ori])
    victim_sequence = models.IntegerField(choices=[(i, i) for i in range(1, 13)])
    victim_age = models.IntegerField()
    victim_ethnicity = models.CharField(max_length=10)
    victim_race = models.CharField(max_length=10)
    victim_sex = models.CharField(max_length=10)
