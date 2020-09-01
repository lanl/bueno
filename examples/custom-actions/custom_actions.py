from bueno.public import container
from bueno.public import experiment
from bueno.public import logger


def pre_action(**kwargs):
    logger.emlog('# Entering pre_action')


def post_action(**kwargs):
    logger.emlog('# Entering post_action')

    cmd = kwargs.pop('command')
    stm = kwargs.pop('start_time')
    etm = kwargs.pop('end_time')
    tet = kwargs.pop('exectime')
    out = kwargs.pop('output')

    logger.log(F'Command: {cmd}')
    logger.log(F'Start time: {stm}')
    logger.log(F'End time: {etm}')
    logger.log(F'Total Execution Time (s): {tet}')

    lines = [x.rstrip() for x in out]
    for line in lines:
        if line.startswith('Data 1'):
            d1 = line.split(':')[1]
            logger.log(F'Data 1 is {d1}')
            continue
        if line.startswith('Data 2'):
            d2 = line.split(':')[1]
            logger.log(F'Data 2 is {d2}')
            continue


def main(argv):
    experiment.name('custom-actions')
    container.run(
        './example-application.sh',
        preaction=pre_action,
        postaction=post_action
    )
