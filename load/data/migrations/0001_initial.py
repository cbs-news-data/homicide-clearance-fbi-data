# Generated by Django 4.0.4 on 2022-05-26 12:06

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agencies',
            fields=[
                ('unique_id', models.CharField(max_length=40, primary_key=True, serialize=False, unique=True)),
                ('data_year', models.IntegerField(choices=[(1960, 1960), (1961, 1961), (1962, 1962), (1963, 1963), (1964, 1964), (1965, 1965), (1966, 1966), (1967, 1967), (1968, 1968), (1969, 1969), (1970, 1970), (1971, 1971), (1972, 1972), (1973, 1973), (1974, 1974), (1975, 1975), (1976, 1976), (1977, 1977), (1978, 1978), (1979, 1979), (1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020)])),
                ('ori', models.CharField(max_length=9, validators=[django.core.validators.RegexValidator('^[A-Z]{2}(?:[A-Z]{3}\\d{4}|\\d{7})$')])),
                ('ncic_agency_name', models.CharField(max_length=50)),
                ('state_abbr', models.CharField(max_length=2)),
                ('county_name', models.CharField(max_length=50)),
                ('msa_name', models.CharField(max_length=50)),
                ('city_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='RetA',
            fields=[
                ('unique_id', models.CharField(max_length=40, primary_key=True, serialize=False, unique=True)),
                ('ori_code', models.CharField(max_length=9, validators=[django.core.validators.RegexValidator('^[A-Z]{2}(?:[A-Z]{3}\\d{4}|\\d{7})$')])),
                ('agency_name', models.CharField(max_length=25)),
                ('core_city', models.BooleanField()),
                ('agency_state_name', models.CharField(max_length=6)),
                ('year', models.IntegerField()),
                ('month', models.CharField(max_length=3)),
                ('card', models.CharField(max_length=14)),
                ('category', models.CharField(max_length=255)),
                ('value', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SHRIncidents',
            fields=[
                ('incident_unique_id', models.CharField(max_length=40, primary_key=True, serialize=False, unique=True)),
                ('ori_code', models.CharField(max_length=9, validators=[django.core.validators.RegexValidator('^[A-Z]{2}(?:[A-Z]{3}\\d{4}|\\d{7})$')])),
                ('last_update', models.DateField()),
                ('year', models.IntegerField(null=True)),
                ('homicide', models.CharField(max_length=1)),
                ('situation', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='SHRVictims',
            fields=[
                ('victim_unique_id', models.CharField(max_length=40, primary_key=True, serialize=False, unique=True)),
                ('incident_unique_id', models.CharField(max_length=40)),
                ('year', models.IntegerField()),
                ('ori_code', models.CharField(max_length=9, validators=[django.core.validators.RegexValidator('^[A-Z]{2}(?:[A-Z]{3}\\d{4}|\\d{7})$')])),
                ('victim_sequence', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)])),
                ('victim_age', models.IntegerField()),
                ('victim_ethnicity', models.CharField(max_length=10)),
                ('victim_race', models.CharField(max_length=10)),
                ('victim_sex', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='SHROffenders',
            fields=[
                ('offender_unique_id', models.CharField(max_length=40, primary_key=True, serialize=False, unique=True)),
                ('year', models.IntegerField()),
                ('ori_code', models.CharField(max_length=9, validators=[django.core.validators.RegexValidator('^[A-Z]{2}(?:[A-Z]{3}\\d{4}|\\d{7})$')])),
                ('offender_sequence', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12)])),
                ('offender_age', models.IntegerField(blank=True, null=True)),
                ('offender_circumstance', models.CharField(max_length=10)),
                ('offender_ethnicity', models.CharField(max_length=10)),
                ('offender_race', models.CharField(max_length=10)),
                ('offender_relationship', models.CharField(max_length=10)),
                ('offender_sex', models.CharField(max_length=10)),
                ('offender_subcircumstance', models.CharField(max_length=10)),
                ('offender_weapon', models.CharField(max_length=10)),
                ('offender_weapon_used', models.CharField(max_length=10)),
                ('incident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.shrincidents')),
            ],
        ),
    ]
