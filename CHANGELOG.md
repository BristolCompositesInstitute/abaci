# Changelog

Notable changes to this project are logged here according to release version and date.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
