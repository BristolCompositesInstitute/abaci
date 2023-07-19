---
title: "Developer Notes"
---

__This page contains useful under-the-hood information about abaci for new contributors and developers__


## Implementation Language

Abaci is implemented in Python and designed to be run using an existing __Abaqus Python__ installation:
- To avoid needing to install or redistribute Python for Abaci
- To allow using Abaqus Python libraries for reading ODB files

__Abaqus Python is 2.7, hence Abaci is implemented using Python 2.7__

*It is also for this reason, that any Python dependencies that Abaci uses*
*are bundled and redistributed (under their respective licenses) with Abaci.*


## Repository Structure

- [`.github/workflows`](https://github.com/BristolCompositesInstitute/abaci/tree/main/.github/workflows): *GitHub actions (CI) workflow files*
  - `DeployDocs.yml`: *builds this documentation site (using Sphinx) and deploy to GitHub pages*
  - `MakeInstaller.yml`: *builds installers for Windows and Linux and attach to new GitHub releases*

- [`docs/`](https://github.com/BristolCompositesInstitute/abaci/tree/main/docs): *all source files for this documentation site (written in Markdown using Sphinx)*

- [`example/`](https://github.com/BristolCompositesInstitute/abaci/tree/main/example): *a self-contained example project for using abaci*

- [`media/`](https://github.com/BristolCompositesInstitute/abaci/tree/main/media): *icon files and images used for documentation*

- [`scripts/`](https://github.com/BristolCompositesInstitute/abaci/tree/main/scripts): *abaci launch scripts and installer files*
  - `abaci`: *abaci launch script for Linux*
  - `abaci-installer.nsi`: *script file to generate the Windows installer using the [Nullsoft Scriptable Install System](https://nsis.sourceforge.io/)*
  - `abaci.cmd`: *abaci launch script for Windows*
  - `install`: *Linux installer shell script*
  - `install-windows`: *alternative command line install script for Windows*

- [`src/`](https://github.com/BristolCompositesInstitute/abaci/tree/main/src): *main abaci source files*
  - `abaci/`: *Python source code for Abaci program*
  - `fortran/`: *Fortran code for [generating tests](./how-to-guides/unit-testing.md)*
  - `redist/`: *redistributed (bundled) library dependencies for Abaci*
  - `abaci_main.py`: *main Python entry point for Abaci program*

- [`test`](https://github.com/BristolCompositesInstitute/abaci/tree/main/test): *unit testsuites for abaci*


## Creating a new release

1. Update the version number in `src/abaci/cli.py` (line 23)
2. Update the version number in `README.md`
3. Update the `CHANGELOG.md` file with new release version and changes summary
4. [Create a new release](https://github.com/BristolCompositesInstitute/abaci/releases/new)
   on GitHub with tag set to the new version number (prefixed with `v`)
   - This will trigger a GitHub actions workflow to generate the Windows and Linux installer
     files, and attach them to the new release


