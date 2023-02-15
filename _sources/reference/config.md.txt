---
title: "Configuration Reference"
---

The abaci configuration file stores information about the project such as user subroutine and abaqus job file locations. There is typically one configuration file per user-subroutine per project. 


```{note}
By default, abaci will look for a configuration file named `abaci.toml` in the current directory. Use the `--config` argument to specify an alternative, see [Common Flags](./cli.md#common-flags).
```


## Configuration File Format

The abaci configuration file uses the human-readable TOML format:

- Lines beginning with an octothorp `#` are ignored

- Configuration parameters are written in `key = value` format

- Values can be:
  - numbers, *e.g.* `pi = 3.141`
  - strings denoted by quotes, *e.g.* `name = 'test'`
  - arrays of values denoted by square brackets, *e.g.* `tags = ['test','default']`

- Parameters can optionally be grouped under unique sections denoted by square brackets, *e.g.* `[section-name]`

- Non-unique (repeatable) sections form arrays and are denoted with double square brackets, *e.g.* `[[job]]`

```{seealso}
See <https://toml.io> for the full TOML specification.
```

## Top-level fields

__Example:__

```toml
name = 'project-name'
user-sub-file = 'usersub.f90'
output = 'scratch'
test-mod-dir = 'test'
```

### name

__*string, optional*__

Specifies the name of the project to uniquely identify it when used as a dependency for
another abaci project.

```{note}
The `name` field is mandatory if the project is to be used as a dependency, otherwise
it can be omitted.
```


### user-sub-file

__*string, mandatory*__

Specifies the filename of the abaqus user subroutine to compile.

- The filename is relative to the folder containing the configuration file

### output

__*string, optional*__

Specifies the name of the directory into which compilation and job folders will be placed.

- The output directory is either:
  - a relative path, relative to the current working directory or;
  - an absolute path
- If omitted, the default output directory is a subdirectory called `scratch` in the current working directory
- The output folder is created if it does not exist


### test-mod-dir

__*string, optional*__

Specifies the name of the directory in which test module files are stored.

- The directory is relative to the folder containing the configuration file
- If omitted, the default test module directory is `test` 

```{seealso}
See the [unit tests guide](../how-to-guides/unit-testing.md) for how to
structure and write unit tests for your Abaqus user subroutine.
```

Use the [`test`](./cli.md#abaci-test) subcommand to compile and run these
test subroutines.


### abq-flags

__*string or [string,...], optional*__

String or list of strings specifying additional flags to pass to Abaqus when launching a job.

- This top-level option applies to all jobs in the config file unless it has been overridden
  in the specification of the job

## Jobs list

Array of optional subsections that predefine specific abaqus jobs to run.

__Example:__

```toml
[[job]]
job-file = 'my-abaqus-job.inp'
name = 'job1'
tags = ['test','three_elem']
abq-flags = 'domains'
include = ['job1_extra_inputs.inp']
mp-mode = 'threads'
post-process = '{PY} {ROOT}/scripts/postprocess.py {ODB}'
cluster.mem-per-cpu = '8000M'
cluster.time = '1-00:00:00'
```

### job-file

__*string, mandatory*__

Specifies the path to the abaqus job file (`*.inp`).

- Job file path is specified relative to the folder containing the configuration file

### name

__*string, optional*__

An unique name to reference this job in the *job-spec* at the command line.

### tags

__*string or [string,...], optional*__

An list of non-unique tags to reference groups of jobs in the *job-spec* at the command line.

### abq-flags

__*string or [string,...], optional*__

String or list of strings specifying additional flags to pass to Abaqus when launching a job.

- This option overrides the top-level default for this job only
- Use the top-level `abq-flags` option to set the default for all jobs

### include

__*string or [string,...], optional*__

An list of additional files to copy to the job folder before launching the job.

- Include file paths are specified relative to the folder containing the configuration file

```{note}
Abaci will automatically detect and copy `.inp` files in the same folder as the job file - use the `include` field to specify
other files that also need to be copied to the job folder for running the job.
```

### mp-mode

__*string, optional*__

An optional field taking the value of either `'threads'` (default), `'mpi'` or `'disable'` to indicate the parallel mode to execute in abaqus (corresponds to the `-mp_mode` command line flag).

If `mp-mode` is `'disable'`, then the abaci command line option for multiple processors will be ignored for this job, it will always run in serial.

### cluster.

__*subsection, optional*__

Override the default options for submitting this job to a cluster via SLURM.

See [cluster options](#cluster-section) below for more information on the cluster option fields.


### post-process

__*string or [string,...], optional*__

An optional field specifying one or more post-processing commands to run once the job has completed.

Specify multiple commands as a list ( _e.g._ `['command_1.sh', 'command_2.sh']`) where each command is run sequentially in order.

The field takes the form of a command to execute and allows certain variables to be used:

- `{PY}` will be substituted with the correct `abaqus python` command
- `{ROOT}` will be substituted with the path to the directory containing the `abaci.toml` configuration file; this allows you to specify the path to your postprocessing script relative to the repository root
- `{ODB}` will be substituted with the path to the output database (`.odb`) file for this job
- `{DIR}` will be substituted with the path to the output directory for this job
- `{JOB}` will be substituted with the name of the job (without any extensions or paths)
- `{REF}` will be substituted with the path to the [`check.reference`](#checkreference) file
- `{NAME}` will be substituted with the job [`name`](#name-1) file

```{seealso}
See the [Post-processing Guide](../how-to-guides/post-processing.md) for more information on how to set up
post-processing commands.
```

```{note}
You can run and rerun post-processing commands for completed jobs using the command [`abaci post <job-dir>`](cli.md#abaci-post) where `<job-dir>` is the output directory for the abaci job that has completed.
```

### check.

__*subsection, optional*__

An optional group for detailing regression checks.

__Example:__

```toml
[[job]]
job-file = 'job.inp'
check.reference = 'reference-output.pkl'
check.steps = ['Step-1']
check.fields = ['SDV1','SDV2']
check.frames = 'last'
check.elements = 'all'
```

#### check.reference

__*string, mandatory*__

Specifies the reference file to compare output against. This is a binary Python pickle file
that contains data from a previous reference run.
If the file does not exist, then it is created using the current run.

The following special variables can be used in this field:

- `{NCPU}` will be substituted with the number of CPUs used to run the job

```{note}
It is recommended to include `{NCPU}` in __check.reference__ when performing
regression checks on multicore jobs due to unavoidable variations that occur
between results produced with different numbers of CPUs
```

#### check.steps

__*[string,...], mandatory*__

List of strings specifying Abaqus job steps for which to check output.

#### check.fields

__*[string,...], mandatory*__

List of strings specifying Abaqus output field variables to check.

#### check.frames

__*strings or [int,...], optional*__

Either a list of frame indices for which to perform checks or `'all'` or `'last'`.

If not specified, then `'last'` is the default.


## Compile section

__*subsection, optional*__

An optional subsection that details compilation settings.

__Example:__

```toml
[compile]
fflags.windows = ''
fflags.linux = ''
cflags.windows = ''
cflags.linux = ''
lflags.windows = ''
lflags.linux = ''
compiletime-checks = false
include = ['extra-source.f90']
sources = ['cpp_functions.cpp']
```

### fflags.windows / fflags.linux

__*string or [string,...], optional*__

Extra compilation flags to pass to the fortran compiler.

- Flags specified here are appended to the Abaqus defaults

### cflags.windows / cflags.linux

__*string or [string,...], optional*__

Extra compilation flags to pass to the c/c++ compiler (auxilliary sources only).

### lflags.windows / lflags.linux

__*string or [string,...], optional*__

Extra link flags to pass to the shared library linker.

- Flags specified here are appended to the Abaqus defaults

### opt-host

__*boolean, optional*__

Whether to compile with host-specific optimisations (**default: `false`**). Disable if distributable binaries are required.

```{note}
Host-specific optimisations may provide additional speedup, however there are some known incompatibilities with using host-specific optimisation from newer Intel compilers due
to how Abaqus vendors fixed versions of Intel shared libraries
```

See [Intel Compiler Developer Guide: xHost](https://www.intel.com/content/www/us/en/develop/documentation/fortran-compiler-oneapi-dev-guide-and-reference/top/compiler-reference/compiler-options/code-generation-options/xhost-qxhost.html) for more information.

### compiletime-checks

__*boolean, optional*__

Whether to always perform strict compile-time checks.

See [Intel Fortran Compiler Developer Guide: warn](https://www.intel.com/content/www/us/en/develop/documentation/fortran-compiler-oneapi-dev-guide-and-reference/top/compiler-reference/compiler-options/compiler-diagnostic-options/warn.html) for more information on compile-time checks.

### include

__*string or [string,...], optional*__

String or list of strings specifying additional files that are included (with `#include`) in the user subroutine file.

```{note}
Abaci will automatically detect Fortran source files in the same directory as your main user subroutine file as include files - use the `include` field to specify source files in other folders that need to be included into your user subroutine.
```

- Included file paths are specified relative to the folder containing the configuration file
- File globbing is supported, _e.g._: `include = 'include/*.f'`
- Sources specified here are automatically made available to other projects that use your project as an Abaci dependency

### sources

__*string or [string,...], optional*__

String or list of strings specifying additional c/c++ source files that are to be compiled and linked with the main user subroutine file.

- Included file paths are specified relative to the folder containing the configuration file
- File globbing is supported, _e.g._: `sources = 'src/*.cpp'`
- Sources specified here are automatically compiled with other projects that use your project as an Abaci dependency


## Cluster section

__*subsection, optional*__

An optional subsection that details default values for submitting jobs
to a cluster via SLURM.

Options specified in this section can be overridden on a per-job basis
by providing them within each job table or by running the `submit` command
interactively (`--interactive`).

```{note}
The multiprocessing mode (`mp_mode`) is specified separately on a
per-job basis using the [`mp-mode` job field](#mp-mode).
```

__Example:__

```toml
[cluster]
time = '0-01:00:00'
nodes = 1
tasks-per-node = 14
cpus-per-task = 1
mem-per-cpu = '4000m'
email = 'ab12345@bristol.ac.uk'
```

### time

__*string, optional*__

Specifies the maximum time limit to request for the job. Format: `days-hours:minutes:seconds`.

If not specified, default is 1 hour if not specified.

### partition

__*string, optional*__

Specifies the cluster partitiion to which to submit the job.

If not specified, default is to let SLURM choose the most appropriate partitiion.

### nodes

__*integer, optional*__

Specifies the number of nodes to request for the job.
This option is only valid if [`mp-mode`](#mp-mode) is `'mpi'`,
otherwise it is ignored and set to `1`.

If not specified, default is `1`.

### tasks-per-node

__*integer, optional*__

Specifies the number of separate tasks to allocate per node for the job.

This option is only valid if [`mp-mode`](#mp-mode) is `'mpi'`,
otherwise it is ignored and set to `1`.

If not specified, default is `1`.

### cpus-per-task

__*integer, optional*__

Specifies the number of processors to allocate per task for the job.

This option is only valid if [`mp-mode`](#mp-mode) is `'threads'`,
otherwise it is ignored and set to `1`.

### mem-per-cpu

__*string, optional*__

Specifies the amount of memory to request per CPU/task for theh job.

If not specified, default is `'4000M'` (4000 MB).

### email

__*string, optional*__

Specifies an email address to which to send job termination notifications.

If not specified, default is for no email notifications.


## Dependency list

__*subsection, optional*__

Array of optional subsections that specify third-party repositories from
which to include additional source files.

__Example:__

```toml
[[dependency]]
name = 'demo-dependency'
git = 'git@github.com:BristolCompositesInstitute/demo-dep.git'
version = '<commit|tag>'
```

```{note}
The dependency must have an `abaci.toml` file in the repository root that specifies a project
`name` and the `include` field in the `[compile]` subsection.
```

### name

__*string, mandatory*__

The name of the dependency used to uniquely identify it and organise its source files.

```{caution}
The `name` field must match the top-level `name` field in the corresponding `abaci.toml` file in the dependency repository.
```

To include source files from a dependency into your Fortran source, prefix the source file path
with the dependency name, _e.g._:

```fortran
#include '<dependency-name>/source-file.f'
```

```{hint}
To view a list of available source files to include, run `abaci show sources` at the command line.
```

### git

__*string, mandatory*__

The remote url to the upstream git repository from which to fetch the dependency.

### version

__*string, mandatory*__

A commit hash or tag specifying the exact version to fetch from the upstream repository.

__Note:__ Abaci will automatically refetch the dependency if this field changes.

```{caution}
It is possible to specify a branch name for `version`, however this is __not recommended__ since
the dependency is not 'pinned' to a specific snapshot; this can cause sudden breaking changes and
prevents other users of your code from reproducing your configuration. If you specify a branch, then
abaci will fetch the latest changes from the branch everytime it is run.
```
