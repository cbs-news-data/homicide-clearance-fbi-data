GENERATED_FILES: output/reta_master.csv

.PHONY: all clean

all: $(GENERATED_FILES)

output/reta_master.csv: \
		src/transform_reta.py \
		input/reta_master.csv \
		$(wildcard hand/*.yaml) # any yaml files in hand are used to replace values
	python $^ $@

clean:
	rm -f output/*