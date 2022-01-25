'''
Used in bueno extras test
'''

from bueno.public import logger


def say_hello():
    '''
    Says hello.
    '''
    logger.log(f'hello from {__name__}')
