#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Tests for container.run()
'''

from bueno.public import container
from bueno.public import experiment
from bueno.public import host
from bueno.public import logger
from bueno.public import metadata

experiment.name('test-shellcmds')


def main(argv):
    fname = 'afile.txt'
    logger.log('# Testing globbing...')
    shargs = {
        'echo': True
    }
    # Wildcards need to be escaped with a `\' or quoted to protect them from
    # expansion by the host.
    container.run('ls \\*')
    # shell and container interfaces should behave as identically as possible.
    host.run('ls \\*', **shargs)

    logger.emlog('# Testing redirection...')
    logger.log('# Adding text to {}:'.format(fname))
    container.run('echo "Some Text" | tee {}'.format(fname))
    container.run('echo "More \'Text\'" >> {}'.format(fname))

    logger.emlog('# The contents of {} are:'.format(fname))
    host.run('cat {}'.format(fname), **shargs)

    logger.emlog('# Testing quoting...')
    container.run('echo "Some \'Text\'"')

    logger.emlog('# Testing command chaining...')
    container.run('true && echo true!')
    container.run('false || echo false... && echo and done!')

    metadata.add_asset(metadata.FileAsset(fname))
