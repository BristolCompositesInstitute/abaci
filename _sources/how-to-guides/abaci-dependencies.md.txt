---
title: "How to Reuse Code from other Abaci Projects"
---

Abaci makes it easy to reuse code from other Abaci compatible repositories.

This is useful for keeping common code centralised in separate repositories and
therfore avoid code-duplication across multiple projects.

Using abaci dependencies to centralise common code also makes it easier to push
updates to multiple projects that depend on the same common code.

__Prerequisites:__ you must have Git installed and available at the command line


## Setup a Project for Reuse

If you would like to reuse code from a _source project_, that project must
first satisfy the following criteria:

1. Be accessible via a git remote repository (_e.g._ GitHub/GitLab)
2. Have an `abaci.toml` configuration file in the repository root folder that contains:
   - a `name` field in the `abaci.toml` AND;
   - source files specified in the `include` or `sources` fields


```{important}
You cannot use code from the top-level user subroutine of a _source project_,
only from source files that it specifies in the `include` and `sources` section
of the configuration file.
- This is to avoid multiple definition of the main user subroutine interface
  (_i.e._ `vumat`,`vdisp`,`vexternaldb`)
- If you have a top-level user subroutine file, you should modularise your
  code so that reusable functions and subroutines are in separate module files.
  See [Using Fortran Modules](https://bristolcompositesinstitute.github.io/RSE-Guide/abaqus-user-subroutines/using-fortran-modules.html).
```


## Using a Remote Dependency

Once you have a _source project_ setup as described above, you can specify it
as a remote dependency in the configuration file `abaci.toml` as follows:

```toml
[[dependency]]
name = "<name>"
git = "<git-url>"
version = "<tag|commit>"
```

Where:
- `<name>` matches the `name` field in the _source project_
- `<git-url>` is the url address for the _source project_ remote repository on GitHub or GitLab
- `<tag|commit>` is either a version tag or git commit hash from the remote repository

__Example:__

```toml
[[dependency]]
name = 'matrix-utils'
git = 'git@github.com:BristolCompositesInstitute/matrix-utils-library.git'
version = '001a415b2e587ee545b1cd69169699f9eed77a65'
```

Once you have updated your `abaci.toml` configuration file, you can verify that
the dependency has been specified correctly by running the command:

```text
  abaci show sources
```

to show a list of source files available. You should see a list of source files
in the current project as well as source files provided by the _source project_
dependency.

__Example:__
```text
  abaci show sources
   [user-sub] usub.f
   [included] CDM_functions.f90
   [included] matrix-utils/matrix_lib.f90
```

__Note:__ files from the _source project_ will be in a subfolder named after
 the _source project_ `name`

Once you have checked that dependency source files are available, you should `include` them
into your top-level user subroutine file - __don't forget to prefix the filenames__
__with the _source project_ name and a forward-slash__:

__Example:__

```c
#include "matrix-utils/matrix_lib.f90"
```


## Notes on using Dependencies

- If the `version` field for the dependency changes, then abaci will automatically
  fetch the updated version, unless you have modified the dependency source files

- Source files for the dependencies are downloaded into a `dependencies` folder
  - You may modify source files for dependencies to get it working with your code,
    however you should always push these changes to the original _source project_
    repository so that they can be accessed by other users

- If your dependency requires a username and password to access, consider using
  SSH to specify the dependency URL instead of HTTPs, see
  [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/about-ssh)
   for more information.