from bueno.public import logger
from bueno.public import experiment

experiment.name('hello-world')


def main(argv):
    logger.log('hello world')
