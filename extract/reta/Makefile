SHELL := /bin/bash

GENERATED_FILES: output/reta_master.csv

all: $(GENERATED_FILES)

.PHONY: all input clean

input:
	cd input ; \
	if [[ $$(ls) != "" ]] ; then \
		rm  * ; \
	fi ; \
	for file in $$(ls -d ../../../raw/reta/*) ; do \
		ln -sf $$file ; \
	done

output/reta_master.csv: \
		hand/fwf-schema.csv \
		$(wildcard input/*)
	@i=0 ; \
	for file in $(wordlist 2, 999, $^) ; do \
		if [ $$i == 0 ] ; then \
			cat $$file | in2csv --encoding ascii -f fixed --schema $< > $@ ; \
		else \
			cat $$file | in2csv --encoding ascii -f fixed --schema $< | awk "NR > 1" >> $@ ; \
		fi ; \
		echo EXTRACT FILE TO CSV $$file; \
		i=$$((i+1)) ; \
	done; \
	echo "Successfully extracted and merged $$(cat $@ | wc -l) rows to $@" > output/extract.log

clean:
	rm -f output/*