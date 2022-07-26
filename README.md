# Abaci

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Test](https://github.com/BristolCompositesInstitute/abaci/actions/workflows/Test.yml/badge.svg)](https://github.com/BristolCompositesInstitute/abaci/actions/workflows/Test.yml)

__A helper utility for compiling, running and testing abaqus user subroutines and jobs.__

__Author:__ Laurence Kedward

__Maintainer:__ laurence.kedward@bristol.ac.uk

__Status:__ v0.4.2 beta

### Key Features:

- Pre-compile user subroutines (using abaqus make)
  - Supports compilation and linking of auxiliary c/c++ sources
- Customise compilation procedure with compiler flags
  - Enable 'debug' mode for catching common errors
  - Perform code coverage to identify executed lines of code
- Prescribe and run benchmark problems as test cases
  - Perform regression checks on output database results
  - Automatically run post-processing commands and scripts
- Submit jobs to a cluster via SLURM with an easy interface
- Specify dependencies to reuse code from other abaci projects

## 1. Getting Started

### 1.1 Requirements

- Abaqus
- Intel Fortran Compiler

__Note:__ To use abaci, the Intel Fortran compiler needs to be available within your command line environment.
On Windows you can use the *'Abaqus Command + iFort'* link from the start menu to ensure this.
On Linux, you can add the appropriate environment module or source the `setvars` script from your Intel compiler installation. 

### 1.2 Installers

You can download installers for Windows and Linux from the [Latest Release](https://github.com/BristolCompositesInstitute/abaci/releases/latest) page. These installers will install abaci for the local user and hence do not require
administrator/root permissions.

The Linux installer will install abaci to `$HOME/.local/bin`, so you should ensure that this folder
is on your path if not already; you can do this by adding the following line to the end of
your `$HOME/.bash_profile` file:

```bash
export PATH=$PATH:$HOME/.local/bin
```

You can check your installation by opening a new command window, or logging in again, and running the command `abaci --version` or `abaci --help`.

### 1.3 Install from Source

If you are developing abaci and you would like to test local changes, then you can
install abaci from the cloned repository by running the install scripts located in
the `scripts` folder.

__On Windows__, this script is called `install-windows.cmd` and this assumes your Abaqus commands folder is `C:\SIMULIA\Commands` as this is where the abaci launcher is placed.
An `uninstall-windows.cmd` script is also provided in the `scripts` folder to remove an existing abaci installation.

__On Linux__, the install script is called `install` and this will install abaci to `$HOME/.local/` so you should
check that `$HOME/.local/bin/` folder is on your path and follow the instructions above if not.


## 2. Usage

Information about the user subroutine file(s) and benchmark problems are stored in a configuration file, `abaci.toml`.
See the [configuration reference documentation](config-reference.md) for more information on what goes in the config file.

Given a configuration file `abaci.toml` in the current directory, abaci is invoked at the command line and accepts a number of different subcommands:

<details>
<summary>Click for full help text</summary>
  
```
usage: abaci [-h] [-V] [--update [[REPO:]GITREF]] {post,submit,run,compile,show,init}

Utility for compiling and running abaqus jobs with user subroutines

positional arguments:
  {post,init,submit,run,compile,show}
                        Subcommand to run
    post                Run regression checks and post-processing scripts for
                        a completed job
    init                Initialise a new abaci.toml project file
    submit              Compile user subroutines and submit jobs to cluster
                        (SLURM)
    run                 Compile user subroutines and run an abaqus job
    compile             Compile user subroutines only
    show                Show useful information about this project

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show abaci version
  --update [[REPO:]GITREF]
                        update abaci from upstream

Run a subcommand with --help to view specific help for that command, for
example: abaci compile --help
```
  
 </details>

### 2.1 `abaci run`

 _Compile user subroutine and run one or more abaqus jobs_

__Example:__
Run all jobs with the `test` tag concurrently:

```
> abaci run -j test
```

<details>
<summary>Click for abaci run help text</summary>
  
```
usage: abaci run [-h] [-v | -q] [--config CONFIG] [-t] [-d] [-0] [-b]
                 [-n NPROC] [-j [NJOB]]
                 [job-spec]

Compile user subroutines and run one or abaqus jobs as described by job-spec

positional arguments:
  job-spec              Either: a comma-separated list of job tags or jobs
                        names to filter jobs specified in the manifest; OR a
                        path to an abaqus job file to run.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         output more information from abaci
  -q, --quiet           output less information from abaci
  --config CONFIG       specify a different config file to default
                        ("abaci.toml")
  -t, --codecov         compile subroutines for code coverage analysis
  -d, --debug           enable run-time debugging checks
  -c, --check           enable strict compile-time checks
  -0, --noopt           compile without any optimisations
  -b, --background      run abaci in the background after compilation
  -n NPROC, --nproc NPROC
                        specify number of threads/processes to run with Abaqus
  -j [NJOB], --jobs [NJOB]
                        run jobs concurrently, optionally specify a maximum
                        number of concurrently running jobs
```
</details>

### 2.2 `abaci compile`

 _Compile user subroutine only_

__Example:__
Compile user-subroutines with runtime debug options:

```
> abaci compile --debug
```

<details>
<summary>Click for abaci compile help text</summary>
  
```
usage: abaci compile [-h] [-v | -q] [--config CONFIG] [-t] [-d] [-0]

Compile user subroutines and exit

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbose    output more information from abaci
  -q, --quiet      output less information from abaci
  --config CONFIG  specify a different config file to default ("abaci.toml")
  -t, --codecov    compile subroutines for code coverage analysis
  -d, --debug      enable run-time debugging checks
  -c, --check      enable strict compile-time checks
  -0, --noopt      compile without any optimisations
```
</details>

### 2.3 `abaci show`

_Show useful information about the current project_

__Example:__
Show a list of jobs in the configuration file

```
> abaci show jobs
```

__Example:__
Show a list of source files that can be 'included':

```
> abaci show sources
```

<details>
<summary>Click for abaci show help text</summary>
  
```
usage: abaci show [-h] [-v | -q] [--config CONFIG] [object [object ...]]

Show useful information about this project

positional arguments:
  object           {config|jobs|dependencies|sources}

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbose    output more information from abaci
  -q, --quiet      output less information from abaci
  --config CONFIG  specify a different config file to default ("abaci.toml")
```
</details>


### 2.4 `abaci post`

_Run or rerun regression checks and post-processing commands for a completed job_

See the [check](config-reference.md#check-options-optional) and [post processing](config-reference.md#post-process-string-optional) configuration options for how to setup post-processing.

__Example:__
Run post-processing for a job in directory `scratch/job_0`

```
> abaci post scratch/job_0
```


<details>
<summary>Click for abaci post help text</summary>
  
```
usage: abaci post [-h] [-v | -q] [--config CONFIG] job-dir

Run regression checks and post-processing scripts for a completed job

positional arguments:
  job-dir          Path to job output directory

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbose    output more information from abaci
  -q, --quiet      output less information from abaci
  --config CONFIG  specify a different config file to default ("abaci.toml")
```
</details>


### 2.5 `abaci submit`

_Prepare and submit a job for running on a cluster via SLURM_

See the [cluster](config-reference.md#cluster-section-optional) configuration options for how to specify job script settings via the configuration file.

__Example:__
Submit all jobs with the 'test' flag using options in the configuration file

```
> abaci submit test
```

__Example:__
Submit the 'static' job and override cluster options interactively at the command line

```
> abaci submit --interactive static
```

<details>
<summary>Click for abaci submit help text</summary>
  
```
usage: abaci submit [-h] [-v | -q] [--config CONFIG] [-t] [-d] [-c] [-0] [-i]
                    [-n]
                    [job-spec]

Compile user subroutines and submit jobs to cluster (SLURM)

positional arguments:
  job-spec           Either: a comma-separated list of job tags or jobs names
                     to filter jobs specified in the manifest; OR a path to an
                     abaqus job file to run.

optional arguments:
  -h, --help         show this help message and exit
  -v, --verbose      output more information from abaci
  -q, --quiet        output less information from abaci
  --config CONFIG    specify a different config file to default ("abaci.toml")
  -t, --codecov      compile subroutines for code coverage analysis
  -d, --debug        enable run-time debugging checks
  -c, --check        enable strict compile-time checks
  -0, --noopt        compile without any optimisations
  -i, --interactive  interactively override job setting defaults before
                     submitting
  -n, --no-submit    prepare job files, but don't submit the batch job
```
</details>


### 2.6 `abaci init`

_Create a new `abaci.toml` configuration file in the current directory_

__Example:__
Create a full configuration file template in the current directory

```
> abaci init --full
```

__Example:__
Create a basic configuration file with a known user subroutine file

```
> abaci init --bare --user usub.f
```


<details>
<summary>Click for abaci init help text</summary>

```
usage: abaci init [-h] [-v | -q] [--config CONFIG] [-f] [-b]
                  [-u CONFIG_USUB_FILE] [-o CONFIG_OUTPUT_PATH]

Initialise a new abaci.toml project file

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         output more information from abaci
  -q, --quiet           output less information from abaci
  --config CONFIG       specify a different config file to default
                        ("abaci.toml")
  -f, --full            output a full set of config options
  -b, --bare            exclude explanatory comments from config
  -u CONFIG_USUB_FILE, --user CONFIG_USUB_FILE
                        specify the user subroutine file path
  -o CONFIG_OUTPUT_PATH, --output CONFIG_OUTPUT_PATH
                        specify the output directory path
```
</details>
