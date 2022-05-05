# Data validation and loading

The code in this folder uses Django's ORM to validate and insert data into a sqlite database, and is therefore structured differently than previous tasks. It's set up similarly to a standard Django project, and this document assumes some knowledge of Django. 

The [input](input/) folder contains symlinks to csv files in the output directories of [transform](../transform) tasks.

[data/models](data/models) contains models for each individual file (return A, shr, etc.).

[data/management/commands](data/management/commands) sets up commands used in [Makefile](Makefile).

[settings.py](settings.py) contains standard Django settings, as well as a CSV_FILES variable that maps the input csvs to the name of the appropriate database model, and a CHUNKSIZE variable that sets the batch size for bulk inserts. 