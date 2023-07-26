# Abaci

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docs Deployed](https://github.com/BristolCompositesInstitute/abaci/actions/workflows/DeployDocs.yml/badge.svg)](https://github.com/BristolCompositesInstitute/abaci/actions/workflows/DeployDocs.yml)

__Abaci is a command line tool for streamlining the development, debugging
and testing of Abaqus user subroutines.__

__Author:__ Laurence Kedward

__Maintainer contact:__ bci-rse@bristol.ac.uk

__Status:__ v0.6.2

__Documentation:__
[bristolcompositesinstitute.github.io/abaci](https://bristolcompositesinstitute.github.io/abaci/)

__Prequisites:__ Abaqus, Intel Fortran Compiler

__Supported Platforms:__ Windows, Linux


### Why use Abaci?

The primary advantage of using Abaci to develop Abaqus user subroutines, is the built-in
__[`debug` mode](https://bristolcompositesinstitute.github.io/abaci/quickstart-tutorial.html#running-a-job-in-debug-mode)__
which compiles your code with extra compile-time and runtime checks enabled.
These checks will __identify memory errors and undefined behaviour that would otherwise go unnoticed__.

Abaci also automates and streamlines many processes involved in code development, including:
- Code compilation under different compiler flags and on different platforms
- Setup and organisation of job file directories
- Writing and running Fortran unit tests
- Running regression checks on output databases
- Running post-processing scripts after jobs have finished
- Compilation and linking of C and C++ source files
- Preparation and submission of SLURM cluster job scripts



## Getting Started

You can download installers for Windows and Linux from the
[Latest Release](https://github.com/BristolCompositesInstitute/abaci/releases/latest)
page. These installers will install abaci for the local user and hence do not require
administrator/root permissions.

- [Installation Guide](https://bristolcompositesinstitute.github.io/abaci/how-to-guides/install.html)
- [Quickstart tutorial](https://bristolcompositesinstitute.github.io/abaci/quickstart-tutorial.html)
- [Command Line Reference](https://bristolcompositesinstitute.github.io/abaci/reference/cli.html)
- [Configuration File Reference](https://bristolcompositesinstitute.github.io/abaci/reference/config.html)
- [How-to Guides](https://bristolcompositesinstitute.github.io/abaci/how-to-guides/index.html)


## License and Use

Abaci is free to use and open source under the MIT license.

__If you find Abaci useful in your own work, please consider giving it a 'star' on Github to let us know.__

You can also email us with any feedback or questions at <bci-rse@bristol.ac.uk>.

If you encounter an issue with Abaci that is not explained in the
[online documentation](https://bristolcompositesinstitute.github.io/abaci/),
feel free to [open an issue](https://github.com/BristolCompositesInstitute/abaci/issues)
in the Github repository or email us directly.
