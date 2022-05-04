SHELL := /bin/bash
SUBDIRS := $(wildcard */.)

.PHONY: all $(SUBDIRS)

all: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

cleanup:
	for d in $(SUBDIRS) ; do \
		cd "$(shell pwd)/$$d" && make cleanup  ; \
	done