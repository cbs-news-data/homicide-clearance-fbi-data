SHELL := /bin/bash
TASKS := extract transform merge load

.PHONY: \
	all \
	raw \
	clean-raw \
	clean-output \
	$(TASKS)

all: $(TASKS)

$(TASKS): venv/bin/activate
	source $< && $(MAKE) -C $@

raw: scripts/cde_download.py
	python $<

venv/bin/activate: requirements.txt
	if [ ! -f $@ ]; then virtualenv venv; fi
	source $@ && pip install -r $<
	touch $@

clean:
	make clean-output
	make clean-raw

clean-raw:
	find . -wholename "./raw/*/*" -type f -delete

clean-output:
	for d in $(TASKS) ; do \
		cd "$(shell pwd)/$$d" && make clean  ; \
	done
