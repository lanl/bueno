#
# Copyright (c) 2020-2022 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Test 1 for experiment.runcmds()
'''

from bueno.public import experiment
from bueno.public import logger


def main(_):
    '''
    main()
    '''
    # Name the experiment.
    experiment.name('runcmds-test')
    cmds = [
        ('srun -n %n', 'srun -n #'),
        ('srun -n %n %n', 'srun -n # #'),
        ('srun -n%n%n', 'srun -n##'),
        ('srun -n noarg', 'srun -n noarg')
    ]
    for cmd in cmds:
        logger.log(f'# Command: {cmd[0]}')
        nfun = 'nidx + 1'
        rcmds = experiment.runcmds(0, 4, cmd[0], nfun)
        for idx, rcmd in enumerate(rcmds):
            exp = cmd[1].replace('#', str(idx))
            logger.log(f'# Expecting {exp}')
            logger.log(f'# Got       {rcmd}')
            assert exp == rcmd
        logger.log('')
