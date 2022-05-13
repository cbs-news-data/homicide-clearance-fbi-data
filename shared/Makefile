# this makefile is used to run all task subdirectories in a given task folder
# it is symlinked to the task directory to avoid repetition

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