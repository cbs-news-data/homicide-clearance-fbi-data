GENERATED_FILES: output/agencies.csv

.PHONY: all clean

all: $(GENERATED_FILES)

output/agencies.csv: \
		input/agencies.csv \
		input/city_names.csv
	csvjoin --left -c ori,ori_code $^ | grep -v ",,,,,,,," > $@
	echo "wrote $$(wc -l $@) total lines to $@. $$(cat output/agencies.csv | csvgrep -c city_name -r ^.+$$ | wc -l) were merged successfully." > output/transform.log

clean:
	rm -f output/*