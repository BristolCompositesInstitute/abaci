---
title: "How-to Write Unit Tests with Abaci"
---

## Introduction

### Why Write Tests?

Writing tests for your code is an important and very useful part of good
software development. Testing code is particularly beneficial for research
software to ensure correctness and avoid mistakes while it is being developed
and updated. 

While developing or updating your user subroutine, the code will likely undergo
many changes; writing tests gives you, and other users of your code, the
confidence that your code is still functioning correctly when you make
changes to your code.

You can learn more about testing in the RSE Guide
[here](https://bristolcompositesinstitute.github.io/RSE-Guide/best-practices/testing.html).

### What are Unit Tests?

```{important}
Unit tests are so-called because they each test only a small part of your code,
*i.e.* one function or subroutine. It is
[__strongly recommended__](https://bristolcompositesinstitute.github.io/RSE-Guide/abaqus-user-subroutines/fortran-style-guidelines.html#subroutines-and-functions)
to organise your user subroutine code into multiple functions or subroutines
which each perform a single job.

__See also:__

- [Single resposibility principle](https://bristolcompositesinstitute.github.io/RSE-Guide/best-practices/single-responsibility.html)
- [Organising Code with Fortran Modules](https://bristolcompositesinstitute.github.io/RSE-Guide/abaqus-user-subroutines/using-fortran-modules.html)
```

### Testing with Abaci

Abaci provides two ways to test your Abaqus user subroutines:

1. Running test jobs and checking/post-processing the outputs
2. Writing unit tests to test individual parts of your code

This guide will explain how to write and run unit tests for your code using
Abaci.


## Writing Tests

### Test Structure

Unit tests with Abaci are written as Fortran subroutines stored in a Fortran
module. Abaci will automatically detect test subroutines that satisfy the
following conditions:

- The subroutine takes no arguments
- The subroutine name begins with `test`
- The subroutine is contained in a module with a name beginning with `test`
- The test module source file is stored in the
[`test-mod-dir`](../reference/config.md#test-mod-dir) directory (default `test`)

```{hint}
You can check if Abaci is detecting your test modules and subroutines correctly,
by running `abaci show tests`.
```

```{note}
There's no need to write a Fortran `program` that runs your test subroutines;
Abaci will automatically generate this for you.
```

__Example:__ _a test module containing one unit test subroutine_

```fortran
module test_elastic
  use Elastic_mod    ! <-- the module that we will test
  implicit none

  contains

  subroutine test_get_properties()
    
    ! Test code goes here

  end subroutine test_get_properties

end module test_elastic
```

```{note}
You __do not__ need to `include` any of your user subroutine source files
in your test module, it will be linked automatically by abaci.
You __do need__ to add `use` statements for any modules that your user subroutine
code is stored in.
```


### Test Code (Assert Methods)

Abaci supplies a copy of the [naturalFruit](https://github.com/cibinjoseph/naturalFRUIT)
testing framework for Fortran which provides a number of useful
[assert methods](https://cibinjoseph.github.io/naturalFRUIT/page/AssertMethods/index.html).

Assert methods allow us to check if a condition is true and report a useful
message if it is not.

To use the naturalfruit assert methods, we simply have to add a `use`
statement to the top of our test module.

__Example:__ _a unit test with assert_equal methods_

```fortran
module test_mod
  use NaturalFruit    ! <-- the testing framework module
  implicit none

  integer, paramter :: a = 1
  real, parameter :: pi = 4*atan(1.0)

  contains

  subroutine test_parameters()

    ! Check that the value of a is one
    call assert_equal(a,1,message="parameter 'a' has an incorrect value")

    ! Check that the value of pi is correct to 4 decimal places
    call assert_equal(pi, 3.141593, tol = 1e-4, message="parameter 'pi' is incorrect")

  end subroutine test_parameters

end module test_mod
```

In this example we use the `assert_equal` method to check the value of two
parameters. In the case of the real variable `pi`, we check the value within
a tolerance by specifying the `tol` argument.

If any assert method fails, it will report a useful message to the screen
along with the name of the test.

```{hint}
The naturalfruit `assert_equal` method accepts `integer`, `real`, `real(dp)`,
`complex` and `complex(dp)` arguments of scalar, 1D or 2D dimension.
Note the first two arguments to `assert_equal` must have the same type
and dimension.
```


### Running the Tests

Given one or more test subroutines conforming to the
[test structure](#test-structure) rules described above, you can easily run
your unit tests at the command line with the [`test`](../reference/cli.md#abaci-test)
subcommand:

```shell
  abaci test
```

Abaci will automatically generate and run a Fortran program to call all of your
unit test subroutines. The output from the assert methods is printed to the
screen.

You can use all the same command line options as for `abaci compile` to control
the compilation settings.

__Example:__ _build and run tests with runtime checks enabled_

```text
  abaci test --debug
```

__Example:__ _build and run tests with code optimizations disabled_

```text
  abaci test --noopt
```


### Code Coverage

```{note}
Code coverage is not yet supported on Windows
```

You can verify how much of your code you are testing by using the `--codecov`
flag at the command line:

```text
  abaci test --codecov
```

After the tests have completed, the resulting code coverage report can be
found in the `<output>/lib` directory.


## Complete Example

In this example we will be using the sample code in the
[`abaqus-modern-fortran`](https://github.com/BristolCompositesInstitute/abaqus-modern-fortran)
repository on Github. This is a simple Abaqus/Standard user subroutine that reproduces
linear elastic behaviour and which has been organised into multiple subroutines
and functions. In this guide, we will write unit tests to check that these
subroutines and functions are running correctly.

We will write a simple test that checks that the
[`get_properties`](https://github.com/BristolCompositesInstitute/abaqus-modern-fortran/blob/b1c9328e3d8de847bf67d3d788db61818bb86fb9/src/Elastic_mod.f90#L51)
subroutine correctly extracts the right property values from the `props`
array.


__`test/test_elastic.f90`:__
```fortran
module test_elastic
  use iso_fortran_env, only: dp=>real64
  use Elastic_mod
  use naturalfruit
  implicit none

contains

  subroutine test_get_props
    
    type(elastic_props_t) :: props
    real(dp) :: props_array(2) = [1.0d9, 0.5d0]

    props = get_properties(props_array)

    call assert_equal(props_array(1), props%e, &
                      message="props%e does not match input array")


    call assert_equal(props_array(2), props%xnu, &
                      message="props%xnu does not match input array")

  end subroutine test_get_props

end module test_elastic

```

We can run the unit test at the command line:

```text
c:\Temp\abaqus-modern-fortran> abaci test
  Log file for this session is "scratch\abaci-64.log"
  Running abaqus make
  Compiling tests
  Running tests

  Test module initialized

      . : successful assert,   F : failed assert

  ..

      Start of FRUIT summary:

  SUCCESSFUL!

  No messages
  Total asserts :              2
  Successful    :              2
  Failed        :              0
  Successful rate:   100.00%

  Successful asserts / total asserts : [            2 /           2  ]
  Successful cases   / total cases   : [            1 /           1  ]
  -- end of FRUIT summary
```


Here we can see that all of our assertions passed and we get a summary of all
the tests.

---

Now let's see what happens if we purposefully swap the `props_array` indices
so that the assertions fail:

```text
c:\Temp\abaqus-modern-fortran> abaci test
  Log file for this session is "scratch\abaci-65.log"
  Running abaqus make
  Compiling tests
  Running tests

  Test module initialized

    . : successful assert,   F : failed assert

  FF

      Start of FRUIT summary:

  Some tests failed!

    -- Failed assertion messages:
    [test_get_props]: Expected [0.500000000000000], Got [1000000000.00000]; User message: [props%e does not match input array]
    [test_get_props]: Expected [1000000000.00000], Got [0.500000000000000]; User message: [props%xnu does not match input array]
    -- end of failed assertion messages.

  Total asserts :              2
  Successful    :              0
  Failed        :              2
  Successful rate:     0.00%

  Successful asserts / total asserts : [            0 /           2  ]
  Successful cases   / total cases   : [            0 /           1  ]
    -- end of FRUIT summary


  (!) Non-zero status return by test driver (1)
```

Now we get a warning that some of our assertions failed and we also get
messages which describe the failed assertions.