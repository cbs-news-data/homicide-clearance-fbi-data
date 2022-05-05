GENERATED_FILES: output/sqlite__temp.db

CSV_FILES := $(wildcard input/*.csv)

.PHONY: all clean

all: $(GENERATED_FILES)

output/sqlite__temp.db: \
		$(CSV_FILES) \
		$(wildcard data/*/*)
	python manage.py load_from_csv $(CSV_FILES)

clean:
	rm -f output/*
	rm -rf data/migrations/*
