# CBS News analysis of FBI homicide data

This repository contains the code for CBS News' 2022 analysis of FBI data related to homicide clearance rates in the US. It includes all files used in this analysis, including code, documentation, and data files. 

## Project Structure

This repository uses [Make](https://www.gnu.org/software/make/) to create a workflow that can be easily reproduced with a single command. 

The project is divided into tasks, each of which is contained in its own directory:

| Task folder         | Description                                                                |
| ------------------- | -------------------------------------------------------------------------- |
| [Extract](Extract/) | Turns the raw annual fixed-width files from the FBI into single csv files. |

*On GitHub, navigate to each task folder for additional documentation of that task.*

### [Raw Data](raw/)

The data files themselves are not uploaded to this repository because they total more than 50gb. Instead, to reproduce this workflow from a fresh clone, run the following:

```shell
make venv/bin/activate
source venv/bin/activate
make raw
```

This runs a series of commands in the [root Makefile](Makefile) that initializes your virtual environment, installs all python dependencies, and downloads the input files to the appropriate folder in [raw/](raw/).

*NOTE: these files are very large and this can take over an hour depending on your internet speed*

### [Scripts](scripts/)

The python files in [scripts/](scripts/) are used to run various stages of the workflow, for example downloading the raw data files. 

### [Frozen](frozen/)

[Frozen/documents/](frozen/documents/) contains PDF files that are not part of the workflow itself but were used in its creation, for example the fixed-with file schemas used in [extract/](extract/).

## How to reproduce

1. Run the steps to download the raw data as described above.
2. Run `make`


