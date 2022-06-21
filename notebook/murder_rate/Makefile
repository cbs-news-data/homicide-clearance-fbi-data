SHELL=/bin/bash

.PHONY: all clean

all: src/murder_rate.ipynb
	ipython $^

clean:
	find output/ -type f -not -name ".gitignore" -delete 
