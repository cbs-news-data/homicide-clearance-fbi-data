SHELL := /bin/bash

GENERATED_FILES: output/agencies.csv
COLUMNS: data_year,ori,ncic_agency_name,state_abbr,population,county_name,msa_name

.PHONY: all clean

.INTERMEDIATE: output/stacked.csv

all: $(GENERATED_FILES)

output/agencies.csv: output/stacked.csv
	head -1 $< > $@
	cat $< | awk "NR > 1" | sort -u >> $@

output/stacked.csv: \
		input/agencies-1960-1999.csv \
		input/agencies-2000-2020.csv
	@i=0 ; \
	for file in $^ ; do \
		if [[ i == 0 ]] ; then \
			cat $$file | csvcut $(COLUMNS) > $@ ; \
		else \
			cat $$file | csvcut $(COLUMNS) >> $@ ; \
		fi ; \
		i=$$((i+1)) ; \
	done ;  \
	echo "Wrote $$(cat $@ | wc -l) unique rows to $@" > output/extract.log
	
clean:
	rm -f output/*