# Abaci

__A helper utility for compiling, running and testing abaqus user subroutines and jobs.__

__Key Features:__

- Pre-compile user subroutines (using abaqus make)
- Customise compilation procedure with compiler flags
  - Enable 'debug' mode for catching common errors
  - Perform code coverage to identify executed lines of code
- Prescribe and run benchmark problems as test cases

__Usage:__

Information about the user subroutine file(s) and benchmark problems are stored in a configuration file, `abaci.toml`.
See the [configuration reference documentation](config-reference.md) for more information on what goes in the config file.

Given a configuration file `abaci.toml` in the current directory, _abaci_ is invoked at the command line and accepts a number of optional arguments:

```
usage: abaci [job-spec] [optional arguments]

Utility for compiling and running abaqus jobs with user subroutines

positional arguments:
  job-spec              Either: a comma-separated list of job tags or jobs
                        names to filter jobs specified in the manifest; OR a
                        path to an abaqus job file to run.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show abaci version
  -v, --verbose         output more information from abaqi
  -q, --quiet           don't output anything from abaqi
  -e, --echo            parse and display the config file, then stop.
  -t, --codecov         compile subroutines for code coverage analysis
  -d, --debug           compile with debug flags
  -c, --compile         compile only, don't run abaqus
  -j JOBS, --jobs JOBS  specify number of mpi jobs to run with Abaqus
  --config CONFIG       specify a different config file to default
                        ("abaci.toml")

```
