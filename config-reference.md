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
- If omitted, the default is '.', ie the current working directory


## Jobs list

Array of optional subsections that predefine specific abaqus jobs to run.

__Example:__

```toml
[[job]]
job-file = 'my-abaqus-job.inp'
name = 'job1'
tags = ['test','three_elem']
include = ['job1_extra_inputs.inp']
mp-mode = 'threads'
```

### `job-file` (*string*, mandatory)

Specifies the path to the abaqus job file (`*.inp`).

- Job file path is specified relative to the folder containing the configuration file ('abaci.toml')

### `name` (*string*, optional)

An optional unique name to reference this job in the *job-spec* at the command line.

### `tags` (*[string]*, optional)

An optional list of non-unique tags to reference groups of jobs in the *job-spec* at the command line.

### `include` (*[string]*, optional)

An optional list of additional files to copy to the job folder before launching the job.

- Include file path is specified relative to the folder containing the configuration file ('abaci.toml')

### `mp-mode` (*[string]*, optional)

An optional field taking the value of either `'threads'` (default), `'mpi'` or `'disable'` to indicate the parallel mode to execute in abaqus (corresponds to the `-mp_mode` command line flag).

If `mp-mode` is `'disable'`, then the abaci command line option for multiple processors will be ignored for this job, it will always run in serial.

### `check` options (optional)

An optional group for detailing regression checks.

__Example:__

```toml
[[job]]
job-file = 'job.inp'
check.reference = 'reference-output.odb'
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


## Compile section (optional)

An optional subsection that details compilation settings.

__Example:__

```toml
[compile]
fflags = ''
debug-symbols = true
runtime-checks = false
compiletime-checks = false
code-coverage = false
include = ['extra-source.f90']
```

### `fflags` (*string*, optional)

Extra compilation flags to pass to the fortran compiler.

### `opt-host` (*bool*, optional)

Whether to compile with host-specific optimisations (**default: `true`**). Disable if distributable binaries are required.

See [Intel Compiler Developer Guide: xHost](https://www.intel.com/content/www/us/en/develop/documentation/cpp-compiler-developer-guide-and-reference/top/compiler-reference/compiler-options/compiler-option-details/code-generation-options/xhost-qxhost.html) for more information.

### `compiletime-checks` (*bool*, optional)

Whether to always perform strict compile-time checks.

See [Intel Fortran Compiler Developer Guide: warn](https://www.intel.com/content/www/us/en/develop/documentation/fortran-compiler-oneapi-dev-guide-and-reference/top/compiler-reference/compiler-options/compiler-option-details/compiler-diagnostic-options/warn.html#warn) for more information on compile-time checks.

### `include` (*string* or *[string]*, optional)

String or list of strings specifying additional files that are included in the user subroutine file.

- Included file paths are specified relative to the folder containing the configuration file ('abaci.toml')
- File globbing is supported, _e.g._: `include = 'src/*.f'`
- Sources specified here are made available to other projects that use your project as a dependency

