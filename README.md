# Abaci

__A helper utility for compiling, running and testing abaqus user subroutines and jobs.__

__Author:__ Laurence Kedward

__Maintainer:__ laurence.kedward@bristol.ac.uk

__Status:__ v0.2.0 beta

### Key Features:

- Pre-compile user subroutines (using abaqus make)
- Customise compilation procedure with compiler flags
  - Enable 'debug' mode for catching common errors
  - Perform code coverage to identify executed lines of code
- Prescribe and run benchmark problems as test cases
  - Perform regression checks on output database results
- Specify dependencies to reuse code from other abaci projects

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

After downloading or cloning the repository, use the `install` script in the `scripts` folder which will install abaci to `$HOME/.local/`.
After running the `install` script, make sure the `$HOME/.local/bin/` folder is on your path if not already;
you can do this by adding the following line to the end of your `$HOME/.bash_profile` file:

```bash
export PATH=$PATH:$HOME/.local/bin
```

You can check your installation by opening a new command windows, or logging in again, and running the command `abaci --version` or `abaci --help`.

## 2. Usage

Information about the user subroutine file(s) and benchmark problems are stored in a configuration file, `abaci.toml`.
See the [configuration reference documentation](config-reference.md) for more information on what goes in the config file.

Given a configuration file `abaci.toml` in the current directory, abaci is invoked at the command line and accepts a number of different subcommands:

<details>
<summary>Click for full help text</summary>
  
```
usage: abaci [-h] [-V] [--update [[REPO:]GITREF]] {run,compile,show} ...

Utility for compiling and running abaqus jobs with user subroutines

positional arguments:
  {run,compile,show}    Subcommand to run
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


