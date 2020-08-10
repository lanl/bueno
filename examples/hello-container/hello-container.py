'''
An example illustrating how to execute commands inside a container.
'''

from bueno.public import container
from bueno.public import experiment
from bueno.public import host


def main(argv):
    experiment.name('hello-container')
    container.run('echo "hello from a container!"')
    host.run('echo "hello from the host!"')
