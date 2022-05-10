GENERATED_FILES: output/agencies.csv

.PHONY: all clean

all: $(GENERATED_FILES)

output/agencies.csv: \
		input/agencies.csv \
		$(wildcard src/*.py)
	python src/transform.py input/agencies.csv > $@

clean:
	rm -f output/*