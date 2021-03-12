'''
An example run script using custom pre- and post-actions.
'''
from bueno.public import container
from bueno.public import experiment
from bueno.public import logger

def pre_action(**kwargs):
    '''
    Actions performed before running the experiment (setup).
    '''
    logger.emlog('# Entering pre_action')


def post_action(**kwargs):
    '''
    Actions performed after running the experiment (analysis).
    '''
    logger.emlog('# Entering post_action')

    cmd = kwargs.pop('command')     # Command string
    out = kwargs.pop('output')      # Output gathered from example-app
    stm = kwargs.pop('start_time')  # Timing values
    etm = kwargs.pop('end_time')
    tet = kwargs.pop('exectime')

    logger.log(F'Command: {cmd}')
    logger.log(F'Start time: {stm}')
    logger.log(F'End time: {etm}')
    logger.log(F'Total Execution Time (s): {tet}\n')

    # It is possible to process the many outputs of the example application.
    lines = [x.rstrip() for x in out]
    for i, line in enumerate(lines):
        # Scan application output for "Data" tag.
        if line.startswith('Data'):
            data = line.split(': ')[1]
            logger.log(F' >> Data {i} is {data}')
            continue

def main(argv):
    experiment.name('custom-actions')
    container.run(
        './example-application.sh', # Application invocation.
        preaction=pre_action,       # Set pre-action callback function.
        postaction=post_action      # Set post-action callback function.
    )
