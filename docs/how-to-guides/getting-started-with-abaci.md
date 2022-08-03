---
title: "Getting Started with Abaci in your Project"
---

To start using Abaci with your User Subroutine project, you will require:

- Your user subroutine source file(s)
- One or more simple test-cases that make use of your user-subroutine


## Organisation and Setup

It is recommended to organise your project with the following folder structure:

```text
.
|-- jobs
|   `-- test-job.inp
|-- scripts
|   `-- post-process.py
`-- src
    |-- utils_mod.f90
    `-- usub.f
```

where:

- User subroutine source files are contained in a `src` folder
  - The top-level user subroutine file is prefixed with `usub_` to indicate
    that it is the main user subroutine for Abaqus
- Abaqus job input files are stored in a separate folder
- Any other scripts, such as for post-processing, are stored in a `scripts` folder


## Initialisation

Abaci requires a configuration file to exist in the top-level project directory
to store useful information about the project. We can automatically generate
one using the [`abaci init`](../reference/cli.md#abaci-init) command.

Using the example project shown above, we can initialise a configuration file
and specify the path to the top-level user subroutine source file:

__Example:__ *initialise config file with path to main user subroutine file*

```shell
  abaci init -u src/usub.f
```

This will create a new configuration file called `abaci.toml` in the current
directory.

```{hint}
- Add the `-b` flag to the `abaci init` command to remove explanatory comments
- Add the `-e` flag to the `abaci init` command to include extra useful config options

See [`abaci init`](../reference/cli.md#abaci-init) for more information.
```

### Multiple Source Files

If your user subroutine code is organised in multiple source files, then abaci
will automatically detect other Fortran source files __in the same directory as
your top-level user subroutine file__.

If you include source files from other folders, then you will need to specify
them in your configuration file using the [`include`](../reference/config.md#include-1)
field in the `[compile]` section.

__Example:__ *source files in a different folder to main user subroutine*

```toml
user-sub-file = 'src/usub.f'

[compile]
include = ['utils/*.f90']
```

```{seealso}
See the BCI RSE guide on modularisation[^fortran_modules] for how to use
Fortran modules to organise your user subroutine code and exploit modern Fortran
interfaces.
```

[^fortran_modules]: <https://bristolcompositesinstitute.github.io/RSE-Guide/abaqus-user-subroutines/using-fortran-modules.html>


### C/C++ Source Files

If your project has C or C++ source files, these can specified using the
[`sources`](../reference/config.md#sources) field in the `[compile]` section.

__Example:__ *specify C++ source files to compile separately*

```toml
user-sub-file = 'src/usub.f'

[compile]
sources = ['src/utils.cpp']
```

You can specify compiler flags for C/C++ source compilation with the
[`cflags`](../reference/config.md#cflagswindows--cflagslinux) fields
in the `[compile]` section.

## Setup Test Jobs 

Once you have a configuration file for your project, you can add your test
job(s) to it so that we can easily run them and test the user subroutine code.


### Add to Configuration File

Again using the example project shown above, we can add the test job to the
configuratin file by opening it up in any text or code editor and adding the
following lines:

```{code-block} toml
---
lineno-start: 1
---
[[job]]
job-file = 'jobs/test-job.inp'
name = 'test-job1'
tags = ['test','1elem']
```

__Explanation:__

- Line `1`: [`[[job]]`](../reference/config.md#jobs-list) indicates the start of a job entry
- Line `2`: [`job-file`](../reference/config.md#job-file) indicates the path to the Abaqus job file (`.inp`)

```{note}
The filepath is specified relative to the location of the configuration file
```

- Line `3`: [`name`](../reference/config.md#name-1) indicates a unique name to refer to this job
- Line `4`: [`tags`](../reference/config.md#tags) are a list of non-unique categories to group similar jobs together


```{hint}
If you add the 'default' tag to any job, then that job will run when no
*job-spec* is given to a command, _e.g._ `abaci run`
```

```{important}
Multiple test jobs are specified by repeating the `[[job]]` entry in the
configuration file.

<details>
<summary>See example</summary>

```toml
[[job]]
job-file = 'jobs/test-job-1.inp'
name = 'job2'
tags = ['test','1elem']

[[job]]
job-file = 'jobs/test-job-2.inp'
name = 'job2'
tags = ['test','1elem']
```

</details>



### Run Jobs

Once our jobs have been added to our configuration file, we can run them
using the [`abaci run`](../reference/cli.md#abaci-run) command.

__Example:__ *run the job named 'test-job1'*

```shell
  abaci run test-job1
```

__Example:__ *run all jobs with the 'test' tag concurrently*

```shell
  abaci run test -j
```

__Example:__ *run all jobs with the 'default' tag and view Abaqus output*

```shell
  abaci run -s
```

In these examples, Abaci will:

1. Compile the user subroutine code, and halt if there is an error 
   - (compilation output files are placed in the `<output>/lib` folder)
2. Create a new job folder in the `<output>` directory for each job
3. Copy job files and the user-subroutine library to each job folder
4. Launch each job with Abaqus and wait for the jobs to complete
5. Run any [regression checks](./regression-checks.md) or
   post-processing scripts if specified

```{note}
By default, the `<output>` folder is called `scratch` in the current directory.
You can change the `<output>` folder using the [`output`](../reference/config.md#output)
configuration option.
```