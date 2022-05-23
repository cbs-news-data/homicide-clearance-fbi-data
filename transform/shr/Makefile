GENERATED_FILES = \
	output/shr_incidents.csv \
	output/shr_offenders.csv \
	output/shr_victims.csv

.PHONY: GENERATED_FILES

GENERATED_FILES: \
		input/shr_master.csv \
		$(wildcard src/*.py)
	python src/transform.py $<

clean:
	rm -f output/*
