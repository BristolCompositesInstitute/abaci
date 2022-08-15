---
title: "Abaci User Documentation"
---

## Introduction

__Abaci is a command line tool for streamlining the development, debugging
and testing of Abaqus user subroutines.__

__Key features:__

- Pre-compile user subroutines using `abaqus make`
- Enable 'debug' mode for catching common code errors
- Supports compilation and linking of C/C++ source files
- Customise compiler flags using a portable configuration file
- Run test case Abaqus models with compiled user subroutine code
  - Perform regression checks on output database results
  - Automatically run post-processing commands for each job
- Easily submit Abaqus jobs to a HPC cluster using SLURM
- Reuse code from other abaci projects as 'dependencies' via git


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
