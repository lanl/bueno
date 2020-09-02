'''
An exaple run script utilizing pre and post actions
'''
from bueno.public import container
from bueno.public import experiment
from bueno.public import logger

# Pre/Post test actions are outlined in a method to be
# used as a callback function when running the container


def pre_action(**kwargs):
    '''
    Actions to be performed before running the application
    (setup)
    '''
    logger.emlog('# Entering pre_action')


def post_action(**kwargs):
    '''
    Actions to be performed after running the application
    (analysis)
    '''
    logger.emlog('# Entering post_action')

    cmd = kwargs.pop('command')  # command sent to terminal
    out = kwargs.pop('output')  # output from example-app
    stm = kwargs.pop('start_time')  # timing values
    etm = kwargs.pop('end_time')
    tet = kwargs.pop('exectime')

    logger.log(F'Command: {cmd}')
    logger.log(F'Start time: {stm}')
    logger.log(F'End time: {etm}')
    logger.log(F'Total Execution Time (s): {tet}\n')

    # it is possible to process the many outputs of the
    # example application
    lines = [x.rstrip() for x in out]
    for i, line in enumerate(lines):

        # screen app output for "Data" tagmy
        if line.startswith('Data'):
            data = line.split(': ')[1]
            logger.log(F' >> Data {i} is {data}')
            continue


def main(argv):
    experiment.name('custom-actions')
    container.run(
        './example-application.sh',  # terminal command/app name
        preaction=pre_action,  # set callback functions
        postaction=post_action
    )
