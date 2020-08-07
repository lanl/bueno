from bueno.public import logger


def say_hello():
    logger.log(F'hello from {__name__}')
