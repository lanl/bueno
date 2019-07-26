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
from bueno.public import container


def main(argv):
    logger.log('# Testing globbing...')
    container.run('ls b*')

    logger.log('# Testing redirection...')
    container.run('echo "Some Text" | tee OUT.txt')
    container.run('echo "More \'Text\'" >> OUT.txt')
    shell.run('cat OUT.txt')

    logger.log('# Testing quoting...')
    container.run('echo "Some \'Text\'"')
