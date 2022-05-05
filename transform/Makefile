SHELL := /bin/bash
SUBDIRS := $(wildcard */.)

.PHONY: all $(SUBDIRS)

all: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	for d in $(SUBDIRS) ; do \
		cd "$(shell pwd)/$$d" && make clean  ; \
	done