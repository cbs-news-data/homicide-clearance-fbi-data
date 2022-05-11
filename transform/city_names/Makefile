GENERATED_FILES: output/city_names.csv

.PHONY: all clean

all: $(GENERATED_FILES)

output/city_names.csv: \
		src/transform.py \
		input/reta_master.csv
	python $^ > $@
	echo "wrote $$(wc -l $@) lines to $@" > output/transform.log

clean:
	rm -f output/*