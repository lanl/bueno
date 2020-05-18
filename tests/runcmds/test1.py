#
# Copyright (c)      2020 Triad National Security, LLC
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


# TODO(skg) Add more tests.
def main(argv):
    # Name the experiment.
    experiment.name('test1-runcmds')
    cmds = [
        'srun -n %n',
        'srun -n %n %n',
        'srun -n%n%n',
        'srun -n noarg',
    ]
    for c in cmds:
        logger.log(F'# Command: {c}')
        nfun = 'nidx'
        rcmds = experiment.runcmds(0, 4, c, nfun)
        for r in rcmds:
            logger.log(F'# {r}')
        logger.log('')
