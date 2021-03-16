# Hello Container

There are different ways to execute commands in bueno run scripts. The following
illustrates the most straightforward way to execute commands targeting both the
container and the host shell (bash-like) emulator.

```Python
from bueno.public import container
from bueno.public import experiment
from bueno.public import host


def main(argv):
    experiment.name('hello-container')
    container.run('echo "hello from a container!"')
    host.run('echo "hello from the host!"')
```

This script can be executed as follows:
```shell
bueno run -a none -p hello-container.py
```

For simplicity, this particular invocation uses the `none` image activator.
Please note that the underlying *container target* in this example is no
more than a pass-through to the host and therefore equivalent to the direct
`host.run()` invocation. We will detail how to change this behavior in an
upcoming example.
