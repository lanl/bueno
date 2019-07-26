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

from bueno.public import logger
from bueno.public import container


def main(argv):
    logger.log('# Testing globbing...')
    # FIXME(skg)
    # container.run('ls b*')

    logger.log('# Testing redirection...')
    container.run('echo "Some Text" | tee OUT.txt')
