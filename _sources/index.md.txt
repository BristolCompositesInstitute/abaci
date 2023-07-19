---
title: "Abaci User Documentation"
---

__Abaci is a command line tool for streamlining the development, debugging
and testing of Abaqus user subroutines.__

## Why use Abaci?

The primary advantage of using Abaci to develop Abaqus user subroutines, is the built-in
__[`debug` mode](quickstart-tutorial.md#running-a-job-in-debug-mode)__ which compiles your code with extra compile-time and runtime checks enabled.
These checks will __identify memory errors and undefined behaviour that would otherwise go unnoticed__.

Abaci also automates and streamlines many processes involved in code development, including:
- [Code compilation under different compiler flags and on different platforms](./reference/config.md#compile-section)
- [Setup and organisation of job file directories](./quickstart-tutorial.md#running-an-abaqus-job)
- [Writing and running Fortran unit tests](./how-to-guides/unit-testing.md)
- [Running regression checks on output databases](./how-to-guides/regression-checks.md)
- [Running post-processing scripts after jobs have finished](./how-to-guides/post-processing.md)
- [Compilation and linking of C and C++ source files](./how-to-guides/cpp-sources.md)
- [Preparation and submission of SLURM cluster job scripts](./how-to-guides/hpc-job-submission.md)


## Getting Started

__Prerequisites:__ Abaci requires the following software to be installed:

- Abaqus
- Intel Fortran Compiler

See the [installation guide](./how-to-guides/install.md) for instructions
on how to download and install Abaci.

Once you have installed Abaci, consider reading the [Quickstart Tutorial](quickstart-tutorial.md) and the [How-to guides](how-to-guides/index.md).


## Documentation and Support

You can find more detailed documentation in the
[Command Line Interface Reference](./reference/cli.md) and the
[Configuration File Reference](./reference/config.md).

If you encounter an problem using Abaci and cannot find the answer using the documentation, then feel free to
[open an issue](https://github.com/BristolCompositesInstitute/abaci/issues)
in the Github repository.



```{toctree}
---
maxdepth: 2
caption: "Contents:"
---
quickstart-tutorial.md
how-to-guides/index
reference/index
```
