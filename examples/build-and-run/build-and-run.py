from bueno.public import container
from bueno.public import experiment
from bueno.public import host
from bueno.public import logger
from bueno.public import utils

import sys
import time


def main(argv):
    experiment.name('nbody-mpi')
    logger.log('# Experiment: {}'.format(experiment.name()))

    prun = host.whichl(['srun', 'mpiexec'])
    if prun is None:
        sys.exit('Cannot find a parallel launcher...')
    app = '/nbody/nbody-mpi'

    # The seemingly strange use of {{}} allows us to first format the string
    # with arguments (the {}) and then generate strings with values passed to -n
    # from the output of range() (the {{}}).
    runcmds = experiment.generate(
        '{} -n {{}}'.format(prun),
        range(1, 3)
    )

    etimes = list()
    for r in runcmds:
        stime = utils.now()
        # TODO(skg) FIXME
        container.prun(r, app)
        etime = utils.now()

        telapsed = etime - stime
        etimes.append(telapsed)
        logger.log(F'# Execution Time: {telapsed}\n')
        # Take a break between runs.
        time.sleep(1)

    logger.log('# Report')
    logger.log('# Command, Execution Time')
    for i in zip(runcmds, etimes):
        logger.log('{}, {}'.format(*i))
