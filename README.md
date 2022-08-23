# Abaci

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Test](https://github.com/BristolCompositesInstitute/abaci/actions/workflows/Test.yml/badge.svg)](https://github.com/BristolCompositesInstitute/abaci/actions/workflows/Test.yml)
[![Docs Deployed](https://github.com/BristolCompositesInstitute/abaci/actions/workflows/DeployDocs.yml/badge.svg)](https://github.com/BristolCompositesInstitute/abaci/actions/workflows/DeployDocs.yml)

__Abaci is a command line tool for streamlining the development, debugging
and testing of Abaqus user subroutines.__

__Author:__ Laurence Kedward

__Maintainer:__ laurence.kedward@bristol.ac.uk

__Status:__ v0.5.0

__Documentation:__
[bristolcompositesinstitute.github.io/abaci](https://bristolcompositesinstitute.github.io/abaci/)

__Prequisites:__ Abaqus, Intel Fortran Compiler

__Supported Platforms:__ Windows, Linux


### Key Features:

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

You can also email us with any feedback or questions at <bci-github@bristol.ac.uk>.

If you encounter an issue with Abaci that is not explained in the
[online documentation](https://bristolcompositesinstitute.github.io/abaci/),
feel free to [open an issue](https://github.com/BristolCompositesInstitute/abaci/issues)
in the Github repository or email us directly.
