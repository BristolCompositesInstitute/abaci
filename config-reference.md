# Abaci configuration reference

The abaci configuration file stores information about the project such as user subroutine and abaqus job file locations.

In particular it allows you to define multiple abaqus jobs and group them by tags.

## Top-level fields

__Example:__

```toml
user-sub-file = 'usersub.f90'
output = 'scratch'
```
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

Specifies the reference `odb` file to compare output against.
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

### `debug-symbols` (*bool*, optional)

Whether to compile with debug symbols.

### `opt-host` (*bool*, optional)

Whether to compile with host-specific optimisations (**default: `true`**). Disable if distributable binaries are required.

See [Intel Compiler Developer Guide: xHost](https://www.intel.com/content/www/us/en/develop/documentation/cpp-compiler-developer-guide-and-reference/top/compiler-reference/compiler-options/compiler-option-details/code-generation-options/xhost-qxhost.html) for more information.

### `runtime-checks` (*bool*, optional)

Whether to compile with runtime checks enabled.

See [Intel Fortran Compiler Developer Guide: check](https://www.intel.com/content/www/us/en/develop/documentation/fortran-compiler-oneapi-dev-guide-and-reference/top/compiler-reference/compiler-options/compiler-option-details/language-options/check.html) for more information on runtime checks.


### `compiletime-checks` (*bool*, optional)

Whether to perform strict compile-time checks.

See [Intel Fortran Compiler Developer Guide: warn](https://www.intel.com/content/www/us/en/develop/documentation/fortran-compiler-oneapi-dev-guide-and-reference/top/compiler-reference/compiler-options/compiler-option-details/compiler-diagnostic-options/warn.html#warn) for more information on compile-time checks.

### `code-coverage` (*bool*, optional)

Whether to instrument code for coverage analysis and generate a coverage report.

### `include` (*string* or *[string]*, optional)

String or list of strings specifying additional files that are included in the user subroutine file.

- Included file paths are specified relative to the folder containing the configuration file ('abaci.toml')


