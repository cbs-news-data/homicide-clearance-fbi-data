SHELL := /bin/bash

GENERATED_FILES: output/shr_master.csv

all: $(GENERATED_FILES)

.PHONY: all cleanup

output/shr_master.csv: \
		hand/fwf-schema.csv \
		$(wildcard input/*)
	@i=0 ; \
	for file in $(wordlist 2, 999, $^) ; do \
		if [ $$i == 0 ] ; then \
			cat $$file | in2csv --schema $< > $@ ; \
		else \
			cat $$file | in2csv --schema $< | awk "NR > 1" >> $@ ; \
		fi ; \
		echo EXTRACT FILE TO CSV $$file; \
		i=$$((i+1)) ; \
	done; \
	echo "Successfully extracted and merged $$(cat $@ | wc -l) rows to $@" > output/extract.log

cleanup:
	rm -f output/*