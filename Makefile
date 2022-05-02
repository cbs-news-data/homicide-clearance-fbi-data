# SHELL := /bin/bash
SUBDIRS := extract

.PHONY: all $(SUBDIRS)

all: $(SUBDIRS)

$(SUBDIRS): venv/bin/activate
	source $< && $(MAKE) -C $@

raw: scripts/download_shr.py
	python $<

venv/bin/activate: requirements.txt
	if [ ! -f $@ ]; then virtualenv venv; fi
	source $@ && pip install -r $<
	touch $@

cleanup:
	for d in $(SUBDIRS) ; do \
		cd "$(shell pwd)/$$d" && make cleanup  ; \
	done