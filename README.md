# bueno: Automated, Reproducible Benchmarking and Analysis

[![Build Status](https://travis-ci.com/lanl/bueno.svg?branch=master)
](https://travis-ci.com/lanl/bueno)

System benchmarking provides a means to compare or assess the performance of
hardware or software against a point of reference. Because of the multitude of
factors that ultimately influence a benchmark’s results, reproducibility is
challenging. To aid in this, we present an extensible software framework named
bueno that provides mechanisms to record and automate many arduous, error-prone
benchmarking tasks: environmental discovery, environmental setup, program
compilation, program execution, data storage, and analysis. More on this later.

## Installation

### User Installation With pip
In a terminal perform the following (assumes a bash-like shell).
```
cd bueno # The directory in which setup.py is located.
python3 -m pip install --user .
```
Add bueno's installation prefix to `PATH`.
```
export PY_USER_BIN=$(python3 -c 'import site; print(site.USER_BASE + "/bin")')
export PATH=$PY_USER_BIN:$PATH
```
Now, the `bueno` command should be available for use.

### User Uninstallation with pip
```
python3 -m pip uninstall bueno
```

## General Usage: Executing a Run Script

### Los Alamos National Laboratory Code Release
C19133 bueno
