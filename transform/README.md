# Data restructuring and cleaning

The code in this folder restructures and cleans the outputs of files in the [extract/](../extract) task folder and writes a single csv file. 

Each individual file process contains the following subdirectories:
- hand: contains yaml files with mappings of values that need to be replaced with standardized values. 
- input: contains a symlink to the appropriate file in the extract task folder
- src: contains 1 or more python scripts used in transformation

*View the README file in each subfolder for additional documentation of that task.*