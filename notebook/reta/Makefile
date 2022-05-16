SHELL=/bin/bash

.PHONY: all clean

all: src/reta.ipynb
	ipython $^

clean:
	find output/ -type f -not -name ".gitignore" -delete 
