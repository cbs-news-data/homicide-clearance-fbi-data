"""contains django configuration settings"""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "sqlite__temp.db",
    }
}

INSTALLED_APPS = ("data",)

SECRET_KEY = "cbs9if+3z32gry6k)wh5#at8a4b316@#a9&w&u17z*80ukc+0l7=b"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

CSV_FILES = {
    "reta_master.csv": "RetA",
}

CHUNKSIZE = 1000
