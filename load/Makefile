GENERATED_FILES: output/sqlite__temp.db

CSV_FILES := $(wildcard input/*.csv)

.PHONY: all migrate clean

all: $(GENERATED_FILES)

output/sqlite__temp.db: \
		$(CSV_FILES) \
		$(wildcard data/*.py) \
		$(wildcard data/*/*.py)
	make clean
	python manage.py makemigrations
	python manage.py migrate --run-syncdb
	python manage.py load_from_csv

clean:
	rm -f output/*
	find . -wholename "./data/migrations/*" ! -name __init__.py -type f -delete
