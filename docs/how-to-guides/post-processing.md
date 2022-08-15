---
title: "How to Setup Post-Processing Commands"
---

Abaci can be easily configured to run post-processing commands after an Abaqus job
has completed.


## Configuration

To add post-processing commands for a particular job file, that job must first be
specified in the configuration file.

__Example:__

```toml
[[job]]
job-file = 'jobs/my-abaqus-job.inp'
name = 'job1'
tags = ['test','1elem']
```

Post-processing commands are easily added to a job by adding the
[`post-process`](../reference/config.md#post-process) field to the job entry:

__Example:__ *adding a post-processing command*

```toml
[[job]]
job-file = 'jobs/my-abaqus-job.inp'
name = 'job1'
tags = ['test','1elem']
post-process = ['python scripts/post-process.py']
```


Multiple post-processing commands can be specified as a list, where each
command is run sequentially in the order listed.

__Example:__ *add multiple post-processing commands*

```toml
[[job]]
job-file = 'jobs/my-abaqus-job.inp'
name = 'job1'
tags = ['test','1elem']
post-process = ['abaqus python scripts/extract-data.py',
                 'python scripts/plot-data.py']
```

Now, once the job has completed execution Abaci will automatically
execute the post-processing commands.

```{hint}
You can run and rerun post-processing commands for completed jobs using the command [`abaci post <job-dir>`](../reference/cli.md#abaci-post) where `<job-dir>` is the output directory for the abaci job that has completed.
```

## Special Variables

There are a number of special variables that can be used in the post-process
commands in order to pass job-specific information to our scripts:

- `{PY}` will be substituted with the correct `abaqus python` command
- `{ROOT}` will be substituted with the path to the directory containing the
  `abaci.toml` configuration file
   - This allows you to specify the path to your postprocessing script relative
     to the repository root
- `{ODB}` will be substituted with the path to the output database (`.odb`)
   file for this job
- `{DIR}` will be substituted with the path to the output directory for this job
- `{JOB}` will be substituted with the name of the job (without any extensions or paths)


__Example:__ *run a python script using Abaqus python*

```toml
[[job]]
job-file = 'myjob.inp'
name = 'myjob'
post-process = '{PY} {ROOT}/scripts/postprocess.py {ODB} {JOB}'
```

This will execute the following command once the job has completed:

```bash
abaqus python /path/to/repo/scripts/postprocess.py /path/to/job-dir/myjob.odb myjob
```

where:
- `{ROOT}` has been replaced with the absolute path to the repository root (defined by the directory containing the abaci.toml file);
- `{ODB}` has been replaced by the absolute path to the output database file;
- `{JOB}` has been replaced by the name of the job.

In this example, the odb filepath and job name have been passed to the script
as a command line arguments. To access them within the Python script, you can
use [`sys.argv`](https://docs.python.org/3/library/sys.html#sys.argv).

__Example:__ *read the first two command line arguments in a Python script*

```python
import sys

odb_file = sys.argv[1]
job_name = sys.argv[2]
```

```{seealso}
See the [Example Project](https://github.com/BristolCompositesInstitute/abaci/tree/main/example)
in the Abaci repository for a full working example of using the post-processing
command.
```