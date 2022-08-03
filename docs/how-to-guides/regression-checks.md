---
title: "How to Setup Regression Checks"
---

Regression checks are useful when updating or refactoring code as a quick
way of ensuring that code changes do not substantially alter the functionality
of the code.

Regression checks in Abaci work very simply by calculating and displaying the
[RMS](https://en.wikipedia.org/wiki/Root-mean-square_deviation) error in field
output variables for all nodes/IPs/elements per frame and step.


```{caution}
Regression checks are recommended for small to medium Abaqus jobs only.

Large Abaqus jobs, with multi-gigabyte output databases, are not suitable for
regression checks due to inefficiencies in the Abaqus Python odb interface.
It is recommended that you write your own post-processing script for large
jobs.
```

## Configuration

To use regression checks for a particular job file, that job must first be
specified in the configuration file.

__Example:__

```toml
[[job]]
job-file = 'jobs/my-abaqus-job.inp'
name = 'job1'
tags = ['test','1elem']
```

Regression checks are enabled for a job by adding the following three
fields to your job entry in the configuration file:

- [`check.reference`](../reference/config.md#checkreference) - *reference file to compare against*
- [`check.fields`](../reference/config.md#checkfields) - *which field output variables to check*
- [`check.steps`](../reference/config.md#checksteps) - *which job steps to check*


__Example:__ *adding regression check options*

```toml
[[job]]
job-file = 'jobs/my-abaqus-job.inp'
name = 'job1'
tags = ['test','1elem']
check.reference = 'jobs/my-abaqus-job-ref.pkl'
check.steps = ['Step-1']
check.fields = ['SDV1','SDV2']
```

In this example, we will store the reference result in a file called
`jobs/my-abaqus-job-ref.pkl` and we will check the first two state
variables for the __last frame__ in `Step-1`.

```{important}
The chosen filename for `check.reference` is unimportant; if this file
does not exist, then Abaci will create it the next time you run this
job. Subsequent runs will then compare against the reference data stored in
that file.

- It is a good idea to store the reference file in the same location as the
  job file.

- The reference file can be added to your Git version control, if not too big,
  so that other users can run regression checks against your results.

```

By default, Abaci will only check values in the __last frame__. To check
values in all frames in the step, you can specify:

```toml
check.frames = 'all'
```

Alternatively, to check specific frames within a step, you can specify
the frame numbers as a list of integers:

```toml
check.frames = [1,99,199]
```


## Running Checks

Once you have enabled regression checks for a particular job in the
configuration file as described above, they will automatically run when you
next run that job.

Remember that if the reference file does not yet exist, then it will be created
on your next run. Subsequent runs will then compare against the reference data
stored in that file.


### Rerunning checks

You can rerun regression checks for a completed job using the
[`abaci post`](../reference/cli.md#abaci-post).

Given a completed Abaci job in the `scratch/myjob_0` directory, then regression
checks can be rerun with:

```shell
  abaci post scratch/myjob_0
```
