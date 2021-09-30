'''
Hello, World! test.
'''

from bueno.public import container
from bueno.public import experiment
from bueno.public import host


def main(_):
    '''
    main()
    '''
    experiment.name('hello-test')
    container.run('echo "hello from a container!"')
    host.run('echo "hello from the host!"')
