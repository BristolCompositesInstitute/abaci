---
title: "Command Line Interface Reference"
---


## Command-Line Overview

Abaci has a number of *subcommands* which are invoked at the command line by:

```shell
  abaci <subcommand>
```

More information about each subcommand can be found on this page in the
respective section.


```{hint}
You can quickly view help text at the command line for any abaci subcommand
by adding the `--help` argument.

__e.g.__ `abaci run --help`
```

```text
usage: abaci

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


### Top-level Operations

__Example:__ *show abaci version and exit*

```shell
  abaci --version
```

__Example:__ *show abaci help text and exit*

```shell
  abaci --help
```

__Example:__ *update abaci installation from the latest main branch*

```shell
  abaci --update
```

__Example:__ *update abaci installation from the latest dev branch*

```shell
  abaci --update dev
```


### Common Flags

The following flags are available for all subcommands:

- __`--help` / `-h`__ - print help for this subcommand
- __`--verbose` / `-v`__ - print more information about what abaci is doing
- __`--quiet` / `-q`__ - suppress all output from abaci
- __`--config`__ - specify a different configuration file to the default


```{note}
For most subcommands, abaci will look for a configuration file named `abaci.toml`
in the current directory. Use the `--config` flag to specify an alternative
configuration file.
```

__Example:__ *use a non-default configuration filename*

```text
  abaci run --config defects-config.toml
```



## `abaci init`

Initialise a new project by generating an abaci configuration file in the
current directory.

```text
usage: abaci init [-h] [-v | -q] [--config CONFIG] [-e] [-f] [-b]
                  [-u CONFIG_USUB_FILE] [-o CONFIG_OUTPUT_PATH]

Initialise a new abaci.toml project file

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         output more information from abaci
  -q, --quiet           output less information from abaci
  --config CONFIG       specify a different config file to default
                        ("abaci.toml")
  -e, --extra           output extra config options
  -f, --force           force overwrite of existing config file
  -b, --bare            exclude explanatory comments from config
  -u CONFIG_USUB_FILE, --user CONFIG_USUB_FILE
                        specify the user subroutine file path
  -o CONFIG_OUTPUT_PATH, --output CONFIG_OUTPUT_PATH
                        specify the output directory path
```

```{note}
`abaci init` will not overwrite an existing configuration file unless the `-f` parameter is given
```

__Example:__ *basic initialisation with path to main user subroutine file*

```
  abaci init -u src/umat.f
```

__Example:__ *initialise with extra configuration options*

```
  abaci init --extra
  abaci init -e
```

__Example:__ *initialise without explanatory comments*

```
  abaci init --bare
  abaci init -b
```

__Example:__ *overwrite an existing configuration file*

```
  abaci init --force
  abaci init -f
```

__Example:__ *initialise a non-default configuration filename*

```
  abaci init --config test-config.toml
```



## `abaci compile`

Compiles main user subroutine and any auxiliary source files.

```text
usage: abaci compile [-h] [-v | -q] [--config CONFIG] [-t] [-d] [-c] [-0] [-g]
                     [-s]

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
  -g, --gcc        use gnu compilers for auxillary source files
  -s, --screen     echo Abaqus output to the screen while running
```

- Compiler output files are placed in `<output>/lib` where `<output>` is the
  output directory specified in the configuration file.

- Abaci will always request a compiler optimisation report from the Intel Compiler;
  this is stored in `<output>/lib/optrpt`

```{note}
By default, abaci will not display compiler output unless there is an error during compilation or linking. You can force the display of compiler output by adding the
`-s` argument.
```

__Example:__ *Basic compilation check*

```text
  abaci compile
```

__Example:__ *Strict compilation checks and show output*

```text
  abaci compile --check --screen
  abaci compile -cs
```

__Example:__ *Use `gcc` for any auxiliary C/C++ sources*

```text
  abaci compile --gcc
  abaci compile -g
```


## `abaci run`

Compiles user subroutine sources and then run one or Abaqus job files.

Compiler-related options behave the same as with [`abaci compile`](#abaci-compile).

```text
usage: abaci run [-h] [-v | -q] [--config CONFIG] [-t] [-d] [-c] [-0] [-g]
                 [-s] [-b] [-n NPROC] [-j [NJOB]]
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
  -g, --gcc             use gnu compilers for auxillary source files
  -s, --screen          echo Abaqus output to the screen while running
  -b, --background      run abaci in the background after compilation
  -n NPROC, --nproc NPROC
                        specify number of threads/processes to run with Abaqus
  -j [NJOB], --jobs [NJOB]
                        run jobs concurrently, optionally specify a maximum
                        number of concurrently running jobs
```

The `job-spec` parameter is either:
- a path to an Abaqus job `.inp` file
- the name of a job specified in the configuration file
- a tag for one or more jobs specified in the configuration file
- a comma-separated list of job names/tags specified in the configuration file

```{note}
If the `job-spec` is omitted, then it is assumed to be `'default'` which will
run any jobs in the configuration file named `'default'` or with the `'default'` tag.
```

Abaqus job files are placed in a folder called `<output>/<name>_<n>` where:
- `<output>` is the output directory specified in the configuration file
- `<name>` is the name of the job
- `<n>` is an integer that is incremented to avoid overwriting existing job files



__Example:__ *run all jobs with the 'default' tag sequentially in debug mode*

```text
  abaci run --debug
  abaci run -d
```

__Example:__ *run a specific job file and print Abaqus output*

```text
  abaci run jobs/test-job.inp --screen
  abaci run jobs/test-job.inp -s
```

__Example:__ *run a job by name specified in the config file with 4 processors*

```text
  abaci run test-job-1 --nproc 4
  abaci run test-job-1 -n 4
```

```{note}
The default multiprocessing mode is `threads`. To use MPI for a job,
you should specify the `mp-mode` field for the job in the configuration file.
```

__Example:__ *run all jobs with the 'test' tag concurrently*

```text
  abaci run test -j
```

__Example:__ *run all jobs with the 'long' tag in the background*

```text
  abaci run long --background
  abaci run long -b
```

```{attention}
Background mode (`--background`/`-b`) is not currently supported on Windows.
```



## `abaci submit`

Compiles user subroutine sources, prepare a SLURM job-script and optionally submit
to SLURM with `sbatch`.

Compiler-related options behave the same as with [`abaci compile`](#abaci-compile).

The `job-spec` parameter is interpreted in the same way as for [`abaci run`](#abaci-run).

```text
usage: abaci submit [-h] [-v | -q] [--config CONFIG] [-t] [-d] [-c] [-0] [-g]
                    [-s] [-i] [-n]
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
  -g, --gcc          use gnu compilers for auxillary source files
  -s, --screen       echo Abaqus output to the screen while running
  -i, --interactive  interactively override job setting defaults before
                     submitting
  -n, --no-submit    prepare job files, but don't submit the batch job
```

```{important}
Cluster settings (nodes, cores, memory) for jobs are specified in the configuration file.
Alternatively, you can use the `--interactive` flag to specify them at the command line.
```

__Example:__ *submit a job named 'big-job' using cluster settings in the configuration file*

```text
  abaci submit big-job
```

__Example:__ *submit a job named 'big-job' and override cluster settings at the command line*

```text
  abaci submit big-job --interactive
  abaci submit big-job -i
```


__Example:__ *prepare job files and SLURM submission script, but don't submit to the cluster*

```text
  abaci submit big-job --no-submit
  abaci submit big-job -n
```

```{seealso}
See the [How-to guide](../how-to-guides/hpc-job-submission.md) for more information on how to
setup and submit jobs to a SLURM cluster.
```


## `abaci post`

Run or rerun regression checks and post-processing commands for a completed job.

```text
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

```{important}
The `abaci post` command does not read from the configuration file - it uses information
that is cached in the job directory. This means that changes to the configuration file
will not affect the behaviour of `abaci post`.
```

```{caution}
The `job-dir` must have been produced by an previous invocation of abaci;
abaci lacks the information required to post-process jobs not run via abaci.
```


## `abaci test`

Compile and run unit tests.

Compiler-related options behave the same as with [`abaci compile`](#abaci-compile).

```text
usage: abaci test [-h] [-v | -q] [--config CONFIG] [-t] [-d] [-c] [-0] [-g]
                  [-s]

Compile user subroutines only and run unit tests

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbose    output more information from abaci
  -q, --quiet      output less information from abaci
  --config CONFIG  specify a different config file to default ("abaci.toml")
  -t, --codecov    compile subroutines for code coverage analysis
  -d, --debug      enable run-time debugging checks
  -c, --check      enable strict compile-time checks
  -0, --noopt      compile without any optimisations
  -g, --gcc        use gnu compilers for auxillary source files
  -s, --screen     echo Abaqus output to the screen while running
```

```{seealso}
See the [unit tests guide](../how-to-guides/unit-testing.md) for how to
structure and write unit tests for your Abaqus user subroutine.
```

__Example:__ _compile and run unit tests_

```text
  abaci test
```


__Example:__ _compile and run unit tests in debug mode_

```text
 abaci test --debug
 abaci test -d
```


__Example:__ _compile and run unit tests with code coverage checking_

```text
 abaci test --codecov
 abaci test -t
```



## `abaci show`

Show useful information about the current project.

```text
usage: abaci show [-h] [-v | -q] [--config CONFIG] [object [object ...]]

Show useful information about this project

positional arguments:
  object           {config|jobs|dependencies|sources|tests}

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbose    output more information from abaci
  -q, --quiet      output less information from abaci
  --config CONFIG  specify a different config file to default ("abaci.toml")
```

__Example:__ *show the internal representation of the configuration*

```text
   abaci show config
```

__Example:__ *show a list jobs specified in the configuration file*

```text
  abaci show jobs
```

__Example:__ *show a list of source files*

```text
  abaci show sources
```

__Example:__ *show a list of unit tests detected by abaci*

```text
  abaci show tests
```

__Example:__ *show a list of third-party dependencies*

```text
  abaci show dependencies
```