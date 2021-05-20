<img src="docs/img/bueno_gray.png" alt="bueno logo" width="210"/>

[![QA](https://github.com/lanl/bueno/actions/workflows/qa.yml/badge.svg)
](https://github.com/lanl/bueno/actions/workflows/qa.yml)

# bueno: Automated, Reproducible Benchmarking and Analysis

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
```shell
cd bueno # The directory in which setup.py is located.
python3 -m pip install --user .
```
Add bueno's installation prefix to `PATH`.
```shell
export PY_USER_BIN=$(python3 -c 'import site; print(site.USER_BASE + "/bin")')
export PATH=$PY_USER_BIN:$PATH
```
Now, the `bueno` command should be available for use.

### User Uninstallation with pip
```shell
python3 -m pip uninstall bueno
```

## Quick Start
After installation, here are some quick examples for getting started.
The following is the *hello world* equivalent of a bueno run script.
This is a simplified version of the example described in more detail
[here](https://lanl.github.io/bueno/html/bueno-run-getting-started.html).
```python
# hello.py
from bueno.public import experiment
from bueno.public import logger

def main(argv):
    experiment.name('hello-word')
    logger.log('hello world')
```
Which is executed by:
```shell
$ bueno run -a none -p hello.py
```

Now, this script can be directly expanded to include other actions,
or with just a few lines, bueno can execute an existing program.
```python
# callbye.py
from bueno.public import experiment
from bueno.public import host

def main(argv):
    experiment.name('call-bye')
    # Execute an existing program via bueno's sh-like shell emulator.
    host.run('python goodbye.py')
```
Where `goodbye.py` is another Python program in the same directory as `callbye.py`.
This example is executed by:
```shell
$ bueno run -a none -p callbye.py
```

## Examples:
* [hello](./examples/hello)
* [hello-container](./examples/hello-container)
* [custom-actions](./examples/custom-actions)
* [metadata](./examples/metadata)
* [extras](./examples/extras)
* [build-and-run](./examples/build-and-run)

### Los Alamos National Laboratory Code Release
C19133 bueno
