SHELL := /bin/bash
TASKS := \
	extract \
	transform \
	merge \
	load \
	notebook

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

clean-raw:
	find . -wholename "./raw/*/*" ! -name ".gitignore" -type f -delete

clean:
	for d in $(TASKS) ; do \
		cd "$(shell pwd)/$$d" && make clean  ; \
	done
