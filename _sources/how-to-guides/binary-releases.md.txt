---
title: "How to Generate Precompiled Binary Releases"
---

It is sometimes useful to generate precompiled binary files for distribution.
This can be easily achieved with abaci using the [`--release`](../reference/cli.md#abaci-compile)
flag.

To generate a binary release, simply run the following command in your abaci project:

```text
  abaci compile --release <release_dir>
```

where `<release_dir>` is the name of a directory in which to place the binary release.
If this directory doesn't exist, abaci will create it for you. You may want to include
the release version in the directory name, _e.g._ `abaci compile --release v1.0`.

Abaci will:
1. Compile you user subroutine source code
2. Copy the compiled binary libraries into your release directory
3. Generate an `abaqus_v6.env` file in the release directory
   - This file tells abaqus where the precompiled subroutine library is


## Cross-platform Release

```{important}
You can only generate precompiled binaries for the platform on which you run abaci.
- Binaries generated on Windows won't work on Linux and _vice versa._
```

Abaci keeps binaries from different platforms in different folders, so you can create
a cross-platform release simply by running abaci on both platforms.

To generate a cross-platform release:
1. Run the `abaci compile --release <dir>` on one platform (_e.g._ Windows)
2. Copy your project folder, including the release directory, to the other platform (_e.g._ Linux)
3. Rerun the `abaci compile --release <dir>` command on the other platform, using
   the same name for `<dir>`

Now the release directory `<dir>` will contain binaries for both Windows and Linux,
and can be distributed to users.


## Running Jobs with Precompiled Binaries

To run an Abaqus job using a precompiled binary release, users should copy the contents
of the release directory into their job directory (folder containing their abaqus job file),
then invoke abaqus as normal.

__Example:__ *Contents of job directory after copying release directory contents*
```
linux64/
win64/
abaqus_v6.env
myjob.inp
```

__Launch abaqus job:__
```
  abaqus job=myjob double=both interactive
```