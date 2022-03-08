# Abaci

__A helper utility for compiling, running and testing abaqus user subroutines and jobs.__

| Author | Maintainer contact | Status |
|--------|--------------------|--------|
| Laurence Kedward | laurence.kedward@bristol.ac.uk | Alpha, under development |

### Key Features:

- Pre-compile user subroutines (using abaqus make)
- Customise compilation procedure with compiler flags
  - Enable 'debug' mode for catching common errors
  - Perform code coverage to identify executed lines of code
- Prescribe and run benchmark problems as test cases
  - Perform regression checks on output database results

## 1. Getting Started

### 1.1 Requirements

- Abaqus
- Intel Fortran Compiler

__Note:__ To use abaci, the Intel Fortran compiler needs to be available within your command line environment.
On Windows you can use the *'Abaqus Command + iFort'* link from the start menu to ensure this.
On Linux, you can add the appropriate environment module or source the `setvars` script from your Intel compiler installation. 

### 1.2 Windows
After downloading or cloning the repository, use the `install-windows.cmd` script in the `scripts` folder
to install abaci into your existing Abaqus installation.
The script assumes your Abaqus commands folder is `C:\SIMULIA\Commands` and this is where the abaci launcher is placed.

After running the `install-windows.cmd` script, you can check your installation by opening a new command window
and running the command `abaci --version` or `abaci --help`.

An `uninstall-windows.cmd` script is also provided in the `scripts` folder to remove an existing abaci installation.

### 1.3 Linux

On linux, add the `./scripts` folder to your path to start using abaci.

## 2.0 Usage

Information about the user subroutine file(s) and benchmark problems are stored in a configuration file, `abaci.toml`.
See the [configuration reference documentation](config-reference.md) for more information on what goes in the config file.

Given a configuration file `abaci.toml` in the current directory, abaci is invoked at the command line and accepts a number of optional arguments:

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
  -v, --verbose         output more information from abaci
  -q, --quiet           output less information from abaci
  -e, --echo            parse and display the config file, then stop
  -l, --list            list jobs specified in config file, then stop
  -t, --codecov         compile subroutines for code coverage analysis
  -d, --debug           compile with debug flags
  -0, --noopt           compile without any optimisations
  -c, --compile         compile only, don't run abaqus
  -b, --background      run abaci in the background after compilation
  --config CONFIG       specify a different config file to default
                        ("abaci.toml")
  -n NPROC, --nproc NPROC
                        specify number of threads/processes to run with Abaqus
  -j [NJOB], --jobs [NJOB]
                        run jobs concurrently, optionally specify a maximum
                        number of concurrently running jobs

On execution, abaci will look for and parse an 'abaci.toml' configuration file
in the current working directory, unless an alternative path has been
specified via the '--config' option. Abaci will then compile the user
subroutine and launch one or more abaqus jobs as specified by the 'job-spec'
argument. If no job-spec is given, then all jobs with the 'default' tag are
run. Regression checks are performed at the end for those jobs with checks
specified.

```
