---
title: "Quickstart Tutorial"
---


## Introduction

This tutorial will explore the workflow of abaci using a simple example project.

### Objectives

In this tutorial you will learn:

1. How to use abaci to compile user-subroutines and run abaqus jobs
2. What output files abaci generates
3. How to provide information to abaci using a configuration file


```{important}
Abaci is a command-line tool - all actions are performed by entering commands into
the Windows command prompt or a Linux shell terminal.
```

## Setup

To follow along with this tutorial you will first need to:

1. Install abaci
2. Check that Abaqus and the Intel Fortran Compiler are available at the command line
3. Clone or download the abaci repository (for the example project)


```{seealso}
See the [installation guide](how-to-guides/install) for how to install abaci on your system
```


### Get the Example Project Files

Once you have established that Abaqus, Intel Fortran and abaci are setup correctly
you can clone the abaci source repository and navigate to the `example` subdirectory:

```shell
  git clone git@github.com:BristolCompositesInstitute/abaci.git
  cd abaci/example
```

The `example` subdirectory contains a complete example of an abaci project including
a simple implicit user subroutine (`src/umat.f`) and a small Abaqus input file (`jobs/test-job.inp`).
The full file structure will look something like this:

```
.
|-- abaci.toml
|-- jobs
|   |-- test-job-results.pkl
|   `-- test-job.inp
|-- scripts
|   `-- post-process.py
`-- src
    |-- Abaqus_Definitions.f90
    `-- umat.f
```
We will use this example project for the remainder of this tutorial.


## Compiling User Subroutine Code

One of the primary roles of abaci is to compile user subroutines for use with Abaqus.
Abaci interfaces with the `abaqus make` command to allow customising the compilation procedure.

Within the example project, you can use abaci to compile a user subroutine with the following command:

```shell
  abaci compile
```

You will notice that a new folder has been created in the `example` directory called `scratch`.
This is the _output folder_ and is where abaci places all generated files during execution.
If we look within this folder we will see a number of files and directories:

```
scratch
|-- abaci-0.log
`-- lib/
    |...
```

Two particular items of importance in the _output folder_ are:

1. `abaci-xx.log` file: _Log files that are created everytime abaci is run to store useful detail about the run_
2. `lib/` folder: _contains the user subroutine source files and compiled library files_

```{hint}
To see more information about what abaci is doing _'behind the scenes'_, you can run
any command with the `--verbose` flag, _e.g._ `$ abaci compile --verbose`

```


```{seealso}
Abaci provides a number of extra command line flags for controlling the compilation process,
including some for identifying bugs in the user-subroutine code.
See the [Command Line Reference](reference/cli.md) for more information, or run:
`$ abaci compile --help`
```

The `compile` subcommand is useful when checking for errors, but it does not allow us to test our
user subroutine with an actual Abaqus job; this is where the `run` subcommand comes in, described in the next section.


## Running an Abaqus Job

The `run` subcommand will do everything that the `compile` subcommand does but it will
also run one or more abaqus jobs after compilation.

Within the example project, you can run an Abaqus job with the following command:

```shell
  abaci run test-job
```

This time, the command will take longer to run and will output more information.

You will also notice that another subfolder called `test-job_0` has been created in the `scratch` _output folder_.
This is the _job folder_ and contains everything required to run an Abaqus job, including the
previously-compiled user subroutines.

```{hint}
Abaci will create a new job folder every time you launch a job by incrementing the numbered suffix.
``` 

In this example, `test-job` is the name of the job we wish to run. We can also specify other job names
or job tags to run a group of jobs.
We can view a list of possible jobs and their tags with the `show` subcommand:

```shell
  abaci show jobs
test-job default,test
```

In this example project, there is only one job called `test-job` and it has the tags `default` and `test`.
We could therefore also run this job with:

```shell
  abaci run test
```

You have now seen how to run abaci from the command line using the example repository,
__but how does abaci know about your code files and abaqus `.inp` job files?__

This information is stored in the `abaci.toml` configuration file, described in the next section.


## The Configuration File

The configuration file is used to store all the information needed by abaci about your user-subroutine code
and test jobs.

When abaci starts, it will look for a configuration file called `abaci.toml` in the current directory.


```{seealso}
_toml_ is a human-readable configuration format, see <https://toml.io/> for more information.
```

If you open the `abaci.toml` file in any code editor, you can see information
about the `example` project including:

- The name of the project
- The name of the _output folder_
- Path to the Fortran user-subroutine source file
- Information about the test-job

You can learn more about individual parts of the configuration file in the
[configuration reference documentation](reference/config).