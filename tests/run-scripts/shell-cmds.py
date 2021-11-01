#
# Copyright (c) 2019-2021 Triad National Security, LLC
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
from bueno.public import data


def main(argv):
    # Name the experiment.
    experiment.name('shellcmds-test')

    fname = 'afile.txt'
    logger.log('# Testing globbing...')
    shargs = {
        'echo': True
    }
    # Wildcards don't need to be escaped with a `\' or quoted to protect them
    # from expansion by the host. We take care of that for you.
    container.run('ls *')
    # host and container interfaces should behave as identically as possible.
    host.run('ls *', **shargs)

    logger.emlog('# Testing redirection...')
    logger.log(F'# Adding text to {fname}:')
    host.run(F'echo "Some Text" | tee {fname}', **shargs)
    host.run(F'echo "More \'Text\'" >> {fname}', **shargs)

    logger.emlog(F'# The contents of {fname} are:')
    host.run(F'cat {fname}', **shargs)

    logger.emlog('# Testing quoting...')
    container.run('echo "Some \'Text\'"')

    logger.emlog('# Testing command chaining...')
    container.run('true && echo true!')
    container.run('false || echo false is good  && echo true is good')

    logger.emlog('# Testing variable lifetimes within chained commands...')
    container.run('export FOO="bar" && '
                  'test ! -z $FOO && '
                  'echo "Looks good!" || '
                  'exit 1')

    data.add_asset(data.FileAsset(fname))
