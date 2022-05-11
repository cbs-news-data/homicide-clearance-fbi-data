GENERATED_FILES: output/reta_master.csv

.PHONY: all clean

all: $(GENERATED_FILES)

output/reta_master.csv: \
		input/reta_master.csv \
		$(wildcard src/*.py) \
		$(wildcard hand/*.yaml) # any yaml files in hand are used to replace values
	python src/transform.py input/reta_master.csv $(wildcard hand/*.yaml) $@

clean:
	rm -f output/*