---
title: "How to Submit Abaci Jobs to a SLURM Cluster"
---

If your project is already setup to run jobs with Abaci, then submitting jobs to a HPC
cluster is easily achieved using the
[`abaci submit`](../reference/cli.md#abaci-submit) command.


__Prerequisites:__ this guide will assume you [have installed abaci](install.md)
(does not require administrator rights) in your home folder on a __SLURM__-based
__Linux__ HPC cluster and have added the relevant module files for Abaqus and the Intel
Fortran compiler.



## Quick Submit (Interactive)

If your project is already [setup](getting-started-with-abaci.md) to use abaci
to run jobs, then you may simply submit a job to the SLURM cluster with the
follow command:

```shell
  abaci submit -i <job>
```

where `<job>` is the path to an Abaqus `inp` file or the name/tag of a job specified
in your configuration file `abaci.toml`.

The [`-i`/`--interactive`](../reference/cli.md#abaci-submit) flag will tell Abaci
to prompt you interactively for various SLURM settings:

```shell
  mp_mode: mpi
  mem-per-cpu: 4000m
  account: aero000001
  partition: compute
  tasks-per-node: 12
  time: 01:00:00
  nodes: 1
  email:
```

Without the [`-i`/`--interactive`](../reference/cli.md#abaci-submit) flag, Abaci
will use default values specified in the configuration file (see next section).


```{tip}
You can use any of the [`abaci compile` command line flags](../reference/cli.md#abaci-compile)
with `abaci submit` to control the compilation process.
```


## Cluster Configuration Defaults

Default values for the various SLURM configuration settings can be specified in
the configuration file (`abaci.toml`) for all jobs and on a per-job basis.

To set defaults for all jobs, add the `[cluster]` section to your configuration file
(__before any `[[job]]` entries__).

__Example:__ *global cluster defaults*

```toml
[cluster]
account = 'aero01234'
partition = 'compute'
email = 'ab12345@bristol.ac.uk'
```

```{seealso}
See the [cluster configuration reference](../reference/config.md#cluster-section)
for more information about each SLURM setting field (behaviour and defaults).
```


To override defaults on a per-job basis, add fields to each `[[job]]` entry
prefixed with `cluster.`

__Example:__ *per-job cluster settings*

```toml
[[job]]
job-file = 'my-abaqus-job.inp'
name = 'job1'
mp-mode = 'threads'

cluster.mem-per-cpu = '8000M'
cluster.time = '1-00:00:00'
```

```{tip}
All jobs inherit defaults from the global `[cluster]` settings unless they
are overridden in the `[[job]]` entry.
```


## MPI vs Threads

Abaci will formulate your SLURM submission script differently depending on whether
you specify `mp_mode=threads` or `mp_mode=mpi` for your job.

### Threads (single-node)

If `mp_mode=threads`, then the SLURM submission script will be formulated for a
single node job with multiple threads.

In this case, the number of threads is controlled by the
[`cpus-per-task`](../reference/config.md#cpus-per-task) configuration field only.

```{note}
When `mp_mode=threads`, then the `nodes` and `tasks-per-node` fields are ignored
and set to `1`.
```

__Example:__ *job configuration for a single-node job*

```toml
[[job]]
job-file = 'my-abaqus-job.inp'
name = 'job1'
mp-mode = 'threads'

cluster.cpus-per-task = 16
cluster.mem-per-cpu = '8000M'
cluster.time = '1-00:00:00'
```

### MPI (single- or multi-node)

If `mp_mode=mpi`, then the SLURM submission script will be formulated for a
multitask MPI job.

In this case, the number of MPI tasks is the product of both:
- [`nodes`](../reference/config.md#nodes) and;
- [`tasks-per-node`](../reference/config.md#tasks-per-node)

```{note}
When `mp_mode=mpi`, then the `cpus-per-task` field is ignored
and set to `1`.
```

__Example:__ *job configuration for a multi-node job*

```toml
[[job]]
job-file = 'my-abaqus-job.inp'
name = 'job1'
mp-mode = 'threads'

cluster.nodes = 4
cluster.tasks-per-node = 16
cluster.mem-per-cpu = '8000M'
cluster.time = '1-00:00:00'
```

In this example, the total number of MPI tasks is `64` (`4x16`).



## Prepare Job Submission Script Only

If you wish to prepare a SLURM job for submission but not submit it to
SLURM straightaway, you can add the [`-n`/`--no-submit`](../reference/cli.md#abaci-submit)
flag.

In this case, abaci will do everything to prepare the job folder and
submission script, but will not submit the job to SLURM.

This allows you to inspect and modify the job submission script if necessary.
The SLURM job script is called `sljob` located in the job folder.

__Example:__ *prepare SLURM job only*

```shell
  abaci submit --no-submit <job>
```


## Environment Modules

When the `abaci submit` command is executed, abaci will take a snapshot
of any environment modules that are currently loaded, and add those
to the job SLURM submission script.

```{important}
You should ensure you have all required environment modules loaded for your
job before running `abaci submit`
```