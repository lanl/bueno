# bueno: Hello Container Example
There are several spaces in which commands can be executed when creating 
bueno run scripts. The following is a basic example of how simple it is
to execute commands in both the container and the host terminal environment.

```Python
from bueno.public import container
from bueno.public import experiment
from bueno.public import host


def main(argv):
    experiment.name('hello-container')
    container.run('echo "hello from a container!"')
    host.run('echo "hello from the host!"')
```

Again, this script can be executed with
```
bueno run -a none -p hello-container.py
```
