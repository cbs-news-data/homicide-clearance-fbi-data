# CBS News analysis of FBI homicide data

This repository contains the code for CBS News' 2022 analysis of FBI data related to homicide clearance rates in the US. It includes all files used in this analysis, including code, documentation, and data files.

## Project Structure

This repository uses [Make](https://www.gnu.org/software/make/) to create a workflow that can be easily reproduced with a single command.

### Tasks

The project is divided into tasks, each of which is contained in its own directory:

| Task folder             | Description                                                                    |
| ----------------------- | ------------------------------------------------------------------------------ |
| [Extract](extract/)     | Turns the raw annual fixed-width files from the FBI into single csv files.     |
| [Transform](transform/) | Cleans the outputs of extract tasks                                            |
| [Merge](merge/)         | Merges any files before loading them                                           |
| [Load](load/)           | Loads the outputs of transformations into a database using Django              |
| [Report](report/)       | Generates reports using Jinja, which are sent to each individual local station |

_View the README file in each task folder for additional documentation of that task._

### [Raw Data](raw/)

The data files themselves are not uploaded to this repository because they total more than 50gb. Instead, to reproduce this workflow from a fresh clone, run the following:

```shell
make venv/bin/activate
source venv/bin/activate
make raw
```

This runs a series of commands in the [root Makefile](Makefile) that initializes your virtual environment, installs all python dependencies, and downloads the input files to the appropriate folder in [raw/](raw/).

_NOTE: these files are very large and this can take over an hour depending on your internet speed_

### [Scripts](scripts/)

The python files in [scripts/](scripts/) are used to run various stages of the workflow, for example downloading the raw data files.

### [Documents](documents/)

[documents/](documents/) contains PDF files that are not part of the workflow itself but were used in its creation, for example the fixed-with file schemas used in [extract/](extract/).

## How to reproduce

_NOTE: This was created using Linux and uses Linux tools, so it will not work from windows unless you run it using [wsl](https://docs.microsoft.com/en-us/windows/wsl/about)._

1. Clone this repository.
2. Run the steps to download the raw data as described above.
3. Run `make`
