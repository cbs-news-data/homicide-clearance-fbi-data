SHELL := /bin/bash

GENERATED_FILES: output/agencies.csv

.PHONY: all clean

.INTERMEDIATE: output/stacked.csv

all: $(GENERATED_FILES)

output/agencies.csv: output/stacked.csv
	head -1 $< > $@
	cat $< | awk "NR > 1" | sort -u >> $@
	echo "Wrote $$(cat $@ | wc -l) unique rows to $@" > output/extract.log

COLUMNS := data_year,ori,ucr_agency_name,ncic_agency_name,state_abbr,population,county_name,msa_name

output/stacked.csv: \
		input/agencies-1960-1999.csv \
		input/agencies-2000-2020.csv
	@i=0 ; \
	for file in $^ ; do \
		if [[ $$i == 0 ]] ; then \
			cat $$file | csvcut -c $(COLUMNS) > $@ ; \
		else \
			cat $$file | csvcut -c $(COLUMNS) | awk "NR > 1" >> $@ ; \
		fi ; \
		i=$$((i+1)) ; \
	done ;  \

clean:
	rm -f output/*