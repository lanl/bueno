#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

from bueno.public import utils
from bueno.public import logger
from bueno.public import container
from bueno.public import experiment

experiment.name('nbody')


def main(argv):
    logger.log('# Executing an MPI Application...')

    prun = 'mpiexec'
    numpe = 2
    app = '/nbody/nbody-mpi'

    stime = utils.now()
    container.run('{} -n {} {}'.format(prun, numpe, app))
    etime = utils.now()

    logger.log('# Execution Time: {} s'.format(etime - stime))
