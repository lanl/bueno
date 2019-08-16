#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Tests for container.run()
'''

from bueno.public import shell
from bueno.public import logger
from bueno.public import metadata
from bueno.public import container
from bueno.public import experiment

experiment.name('test-shellcmds')


def main(argv):
    fname = 'afile.txt'
    logger.log('# Testing globbing...')
    # TODO(skg) FIXME
    container.run('ls -l')

    logger.emlog('# Testing redirection...')
    logger.log('# Adding text to {}:'.format(fname))
    container.run('echo "Some Text" | tee {}'.format(fname))
    container.run('echo "More \'Text\'" >> {}'.format(fname))

    logger.emlog('# The contents of {} are:'.format(fname))
    shell.run('cat {}'.format(fname))

    logger.emlog('# Testing quoting...')
    container.run('echo "Some \'Text\'"')

    metadata.add_asset(metadata.FileAsset(fname))
