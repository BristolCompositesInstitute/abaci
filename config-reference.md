# Abaci configuration reference

The abaci configuration file stores information about the project such as user subroutine and abaqus job file locations.

In particular it allows you to define multiple abaqus jobs and group them by tags.

## Top-level fields

__Example:__

```toml
name = 'project-name'
user-sub-file = 'usersub.f90'
output = 'scratch'
```

### `name` (*string*, optional)

Specifies the name of the project to uniquely identify it when used as a dependency for
another abaci project.

__Note:__ this field is mandatory if the project is to be used as a dependency, otherwise
it can be omitted.


### `user-sub-file` (*string*, mandatory)

Specifies the filename of the abaqus user subroutine to compile.

- Specified relative to the folder containing the configuration file ('abaci.toml')

### `output` (*string*, optional)

Specifies the name of the directory into which compilation and job folders will be placed.

- Specified relative to the current working directory.
- If omitted, the default is `./scratch` (in the current working directory)
- The output folder is created if it does not exist


### `abq-flags` (*string* or *[string]*, optional)

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

### `job-file` (*string*, mandatory)

Specifies the path to the abaqus job file (`*.inp`).

- Job file path is specified relative to the folder containing the configuration file ('abaci.toml')

### `name` (*string*, optional)

An optional unique name to reference this job in the *job-spec* at the command line.

### `tags` (*[string]*, optional)

An optional list of non-unique tags to reference groups of jobs in the *job-spec* at the command line.

### `abq-flags` (*string* or *[string]*, optional)

String or list of strings specifying additional flags to pass to Abaqus when launching a job.

- This option overrides the top-level default for this job only
- Use the top-level `abq-flags` option to set the default for all jobs

### `include` (*[string]*, optional)

An optional list of additional files to copy to the job folder before launching the job.

- Include file path is specified relative to the folder containing the configuration file ('abaci.toml')

### `mp-mode` (*[string]*, optional)

An optional field taking the value of either `'threads'` (default), `'mpi'` or `'disable'` to indicate the parallel mode to execute in abaqus (corresponds to the `-mp_mode` command line flag).

If `mp-mode` is `'disable'`, then the abaci command line option for multiple processors will be ignored for this job, it will always run in serial.

### `cluster.` options (optional)

Override the default options for submitting this job to a cluster via SLURM.

See [cluster options](#cluster-section-optional) below for more information on the cluster option fields.


### `post-process` (*string* or *[string]*, optional)

An optional field specifying one or more post-processing commands to run once the job has completed.
Specify multiple commands as a list ( _e.g._ `['command_1.sh', 'command_2.sh']`) where each command is
run sequentially in order.

The field takes the form of a command to execute and allows certain variables to be used:

- `{PY}` will be substituted with the correct `abaqus python` command
- `{ROOT}` will be substituted with the path to the directory containing the `abaci.toml` configuration file; this allows you to specify the path to your postprocessing script relative to the repository root
- `{ODB}` will be substituted with the path to the output database (`.odb`) file for this job
- `{DIR}` will be substituted with the path to the output directory for this job
- `{JOB}` will be substituted with the name of the job (without any extensions or paths)

__Example:__ run a python script:

```toml
[[job]]
job-file = 'myjob.inp'
name = 'myjob'
post-process = '{PY} {ROOT}/scripts/postprocess.py {ODB} {JOB}'
```

This will execute the following command once the job has completed:

```bash
abaqus python /path/to/repo/scripts/postprocess.py /path/to/job-dir/myjob.odb myjob
```

where `{ROOT}` has been replaced with the absolute path to the repository root (defined by the directory containing the abaci.toml file); `{ODB}` has been replaced by the absolute path to the output database file and `{JOB}` has been replaced by the name of the job.
In the postprocessing script, you can access the values for `{ODB}` and `{JOB}` that were passed as command line arguments using [`sys.argv`](https://docs.python.org/3/library/sys.html#sys.argv).

__Note:__ you can run and rerun post-processing scripts for completed jobs using the command `abaci post <job-dir>` where `<job-dir>` is the output directory for the abaci job that has completed.

### `check` options (optional)

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

#### `check.reference` (*string*)

Specifies the reference file to compare output against. This is a binary Python pickle file
that contains data from a previous reference run.
If the file does not exist, then it is created using the current run.

#### `check.steps` (*[string]*)

List of abaqus job steps for which to check output.

#### `check.fields` (*[string]*)

List of abaqus field variables to check.

#### `check.frames` (*string* or *[int]*, optional)

Either a list of frame indices for which to perform checks or `'all'` or `'last'`.

If not specified, then `'last'` is the default.

#### `check.elements` (*string* or *[int]*, optional)

Either a list of element indices for which to perform checks or `'all'`.

If not specified, then `'all'` is the default.


## Dependency list (optional)

Array of optional subsections that specify third-party repositories from
which to include additional source files.

__Example:__

```toml
[[dependency]]
name = 'demo-dependency'
git = 'git@github.com:BristolCompositesInstitute/demo-dep.git'
version = '<commit|tag>'
```

__Note:__ The dependency must have an `abaci.toml` file in the repository root that specifies a project
`name` and the `include` field in the `[compile]` subsection.

### `name` (*string*)

The name of the dependency used to uniqueuly identify it and organise its source files.

__Note:__ this `name` field must match the top-level `name` field in the corresponding `abaci.toml` file in the dependency repository.

To include source files from a dependency into your Fortran source, prefix the source file path
with the dependency name, _e.g._:

```fortran
      include '<dependency-name>/source-file.f'
```

### `git` (*string*)

The remote url to the upstream git repository from which to fetch the dependency.

### `version` (*string*)

A mandatory commit hash or tag specifying the exact version to fetch from the upstream repository.

__Note:__ Abaci will automatically refetch the dependency if this field changes.

__Note:__ it is possible to specify a branch name for `version`, however this is __not recommended__ since
the dependency is not 'pinned' to a specific snapshot; this can cause sudden breaking changes and
prevents other users of your code from reproducing your configuration. If you specify a branch, then
abaci will fetch the latest changes from the branch everytime it is run.


## Cluster section (optional)

An optional subsection that details default values for submitting jobs
to a cluster via SLURM.

Options specified in this section can be overridden on a per-job basis
by providing them within each job table or by running the `submit` command
interactively (`--interactive`).

__Note:__ the multiprocessing mode (`mp_mode`) is specified separately on a
per-job basis using the [`mp-mode` job field](#mp-mode-string-optional).

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

### `time` (*string*, optional)

Specifies the maximum time limit to request for the job. Format: `days-hours:minutes:seconds`.

If not specified, default is 1 hour if not specified.

### `partition` (*string*, optional)

Specifies the cluster partitiion to which to submit the job.

If not specified, default is to let SLURM choose the most appropriate partitiion.

### `nodes` (*integer*, optional)

Specifies the number of nodes to request for the job.
This option is only valid if [`mp-mode`](#mp-mode-string-optional) is `'mpi'`,
otherwise it is ignored and set to `1`.

If not specified, default is `1`.

### `tasks-per-node` (*integer*, optional)

Specifies the number of separate tasks to allocate per node for the job.

This option is only valid if [`mp-mode`](#mp-mode-string-optional) is `'mpi'`,
otherwise it is ignored and set to `1`.

If not specified, default is `1`.

### `cpus-per-task` (*integer*, optional)

Specifies the number of processors to allocate per task for the job.

This option is only valid if [`mp-mode`](#mp-mode-string-optional) is `'threads'`,
otherwise it is ignored and set to `1`.

### `mem-per-cpu` (*string*, optional)

Specifies the amount of memory to request per CPU/task for theh job.

If not specified, default is `'4000M'` (4000 MB).

### `email` (*string*, optional)

Specifies an email address to which to send job termination notifications.

If not specified, default is for no email notifications.


## Compile section (optional)

An optional subsection that details compilation settings.

__Example:__

```toml
[compile]
fflags.windows = ''
fflags.linux = ''
cflags.windows = ''
cflags.linux = ''
compiletime-checks = false
include = ['extra-source.f90']
sources = ['cpp_functions.cpp']
```

### `fflags.windows` / `fflags.linux` (*string*, optional)

Extra compilation flags to pass to the fortran compiler.

### `cflags.windows` / `cflags.linux` (*string*, optional)

Extra compilation flags to pass to the c/c++ compiler (auxilliary sources only).

### `opt-host` (*bool*, optional)

Whether to compile with host-specific optimisations (**default: `false`**). Disable if distributable binaries are required.

> There are some incompatibilities with using host-specific optimisation from newer Intel compilers due
> to how Abaqus vendors fixed versions of Intel shared libraries

See [Intel Compiler Developer Guide: xHost](https://www.intel.com/content/www/us/en/develop/documentation/cpp-compiler-developer-guide-and-reference/top/compiler-reference/compiler-options/compiler-option-details/code-generation-options/xhost-qxhost.html) for more information.

### `compiletime-checks` (*bool*, optional)

Whether to always perform strict compile-time checks.

See [Intel Fortran Compiler Developer Guide: warn](https://www.intel.com/content/www/us/en/develop/documentation/fortran-compiler-oneapi-dev-guide-and-reference/top/compiler-reference/compiler-options/compiler-option-details/compiler-diagnostic-options/warn.html#warn) for more information on compile-time checks.

### `include` (*string* or *[string]*, optional)

String or list of strings specifying additional files that are included (with `#include`) in the user subroutine file.

Abaci will automatically detect Fortran source files in the same directory as your main user subroutine file as include files - use this field to specify source files in other folders that need to be included into your user subroutine.

- Included file paths are specified relative to the folder containing the configuration file ('abaci.toml')
- File globbing is supported, _e.g._: `include = 'src/*.f'`
- Sources specified here are made available to other projects that use your project as a dependency

### `sources` (*string* or *[string]*, optional)

String or list of strings specifying additional c/c++ source files that are to be compiled and linked with the main user subroutine file.

- Included file paths are specified relative to the folder containing the configuration file ('abaci.toml')
- File globbing is supported, _e.g._: `sources = 'src/*.cpp'`
- Sources specified here are compiled with other projects that use your project as a dependency
