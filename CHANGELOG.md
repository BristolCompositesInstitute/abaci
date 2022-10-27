# Changelog

Notable changes to this project are logged here according to release version and date.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [v0.5.0](https://github.com/BristolCompositesInstitute/abaci/releases/tag/v0.5.0) - 27/10/22

- Add `{REF}` special variable for `check.reference` file in post-processing field
- Add `{NAME}` special variable for `job.name` file in post-processing field
- Fix minor issue with `abq-flags` field when not specified as a list
- Add `test` subcommand for automatically compiling and running unit tests
- Update `show` subcommand with `tests` option to list detected unit tests
- Add `{NCPU}` special variable for number of CPUs in `check.reference` field
- Add support for file globbing in `job.include` field

## [[v0.4.4]](https://github.com/BristolCompositesInstitute/abaci/releases/tag/v0.4.4) - 04/08/22

- Update abaci init config template to include `abq-flags` and `lflags`
- Update abaci init to not overwrite existing files unless requested
- Fix: incorrect compiletime check options for gcc
- Add sphinx documentation to repository

## [[v0.4.3]](https://github.com/BristolCompositesInstitute/abaci/releases/tag/v0.4.3) - 01/08/22

- Fix bug from previous release for running jobs concurrently

## [[v0.4.2]](https://github.com/BristolCompositesInstitute/abaci/releases/tag/v0.4.2) - 28/07/22

- Fix bug with c/c++ compiler flags being set wrong due to list mutation
- Change the default output directory to be `./scratch`
- Automatically add Fortran files in the same folder as the user subroutine file to the include list
- Add `abq-flags` field to config for specifying additional flags for Abaqus launch command
- Add `--screen/-s` flag to echo Abaqus output to the console while running
- Add `lflags` field to config compile table to specify extra linker flags
- Automatically include `.inp` files in the same folder as the job file

## [[v0.4.1]](https://github.com/BristolCompositesInstitute/abaci/releases/tag/v0.4.1) - 11/07/22

- Host-specific compiler optimisations are now disabled by default
- Add new `abaci init` subcommand to initialise a new `abaci.toml` configuration file
- Revert addition of nan initialisation to runtime checking flags since it
  prevents the uninitialised use check

## [[v0.4.0]](https://github.com/BristolCompositesInstitute/abaci/releases/tag/v0.4.0) - 05/07/22

- Minor update to example project post-processing script to avoid warning message
- Add support for separately compile c/c++ sources files via `sources` field
- Separate `fflags` field into `fflags.linux` and `fflags.windows`
- Fix utf-8 encoding issue on Windows using `PYTHONIOENCODING` environment variable
- Add support for multiple post-processing scripts
- Update ifort flags to include `qopenmp` option
- Update ifort flags to include interface checking (`-gen-interfaces`,`-warn interfaces`)
- Update ifort debug flags to initialise NaN
- Update ifort debug flags to remove check for array temporaries unless strict checks enabled
- Update abaqus_v6.env file to print final compile flag combination
- Update abaqus launch flags with `double=both`

## [[v0.3.0]](https://github.com/BristolCompositesInstitute/abaci/releases/tag/v0.3.0) - 20/05/22

- Add new `post` subcommand for (re)running post-processing checks and scripts
- Add new `submit` subcommand for submitting jobs to cluster via SLURM
- Add new cluster options to configuration file for controlling job submission via SLURM
- Add explicit check and error message for missing configuration file


## [[v0.2.1]](https://github.com/BristolCompositesInstitute/abaci/releases/tag/v0.2.1) - 10/05/22

- Minor fix for job specifications with explicit names
- Add example project to repository
- Add CI workflow and scripts for generating installers
- Update `--update` process for when windows launcher is in local app data


## [[v0.2.0]](https://github.com/BristolCompositesInstitute/abaci/releases/tag/v0.2.0) - 28/04/22

_First versioned release._
Major change from alpha: update CLI to use subcommands (abaci run, abaci compile, abaci show)

- Adds testing infrastructure
- Adds support for remote dependencies via git
- Adds support for including source subdirectories
- Refactor code for launching and handling Abaqus jobs
- Adds a check for Abaqus and git (if needed)
- Adds `--update` command for self-updating abaci
- Adds install script for linux
- Adds `--check` flag for enabling compile-time checks
- Remove redundant config fields from compile table

## [v0.1.0] - Alpha (unreleased)

Initial alpha testing version with basic functionality.

First versioned release of the implicit CZM repository.
