SHELL := /bin/bash
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

clean:
	make clean-outputs
	find . -wholename "./raw/*/*" -type f -delete

clean-output:
	for d in $(SUBDIRS) ; do \
		cd "$(shell pwd)/$$d" && make clean  ; \
	done
