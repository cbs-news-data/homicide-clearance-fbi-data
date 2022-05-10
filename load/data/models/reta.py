"""contains models for Return A data"""

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
