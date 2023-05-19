---
title: "How to Include C/C++ Sources"
---


Abaci makes it easier to use C and C++ source files in combination with your Abaqus user subroutine code.
Given a user subroutine file `usub.f`, we can easily compile and link a C or C++ source file
and call that from our user subroutine code.


__Prerequisites:__ in order to compile C and C++ source files, you will need an appropriate compiler, either:
Microsoft C/C++ compiler (Windows only), the Intel C Compiler or the GNU compiler suite (GCC).



## Source Files

Given a C++ source file `lib_functions.cpp` in the `src` folder, we
can tell Abaci about this by adding the following to our configuration file (`abaci.toml`):

```toml
[compile]
sources = ['src/lib_functions.cpp']
```

Abaci will add a separate compilation step to compile any source files specified in this way.
When the main user subroutine file is subsequently compiled with `abaqus make`, the compiled
C/C++ source files are linked in with this.

```{hint}
You can specify multiple C/C++ source files with globbing: `sources=['src/*.c','src/*.cpp']`
```


## Compiler

__On Windows__, C and C++ source files are compiled by default with the Microsoft C/C++ Optimizing Compiler (`cl`).

__On Linux__, C and C++ source files are compiled by default with the Intel C compiler (`icc`).

__To use GCC__ for compiling C and C++ source files, on either Windows or Linux, add the [`--gcc`](../reference/cli.md#abaci-compile)
command line flag.

__Example:__

```shell
  abaci run --gcc
```


### Compiler Flags

To customise the C/C++ compiler flags, you can specify [`cflags`](../reference/config.md#cflags-windows-cflags-linux)
in the configuration file:

__Example:__

```toml
[compile]
cflags.windows = ['/fp:fast']
cflags.linux = ['-fp-model' 'fast']
cflags.gcc = ['-funsafe-math-optimizations']
```

