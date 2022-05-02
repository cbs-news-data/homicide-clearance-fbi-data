# Extraction of fixed-width FBI data files to csv

The code in this folder merges the yearly fixed-width files from the FBI to single comma-delimited files. 

In each folder, there is a hand/ directory containing a file titled "fwf-schema.csv" which tells in2csv how to parse the fields. The column names and positions are hand-created and derived from the PDF files in [documents/](../documents). 

The files in each input/ directory are symlinks to files located in the appriate folder in [raw/](../raw), which are created when running [scripts/cde_download.py](../scripts/cde_download.py) or simply `make raw`. 

