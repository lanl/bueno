'''
Used in bueno extras test
'''

from bueno.public import logger


def say_hello():
    '''
    Says hello.
    '''
    logger.log(F'hello from {__name__}')
