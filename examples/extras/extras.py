from bueno.public import experiment
from bueno.public import logger
from bueno.public import metadata
from bueno.public import utils

try:
    import mymod
    from mypackage import mypackmod
except ImportError:
    pass
else:
    # Because bueno cannot easily determine what extra stuff was imported at
    # run-time, add the extras by hand to our run's metadata.
    metadata.add_asset(metadata.PythonModuleAsset(mymod))
    metadata.add_asset(metadata.PythonModuleAsset(mypackmod))


def main(argv):
    experiment.name('hello-extras')
    logger.log('This is an example of how to use extras')
    # Use the extra modules we specified at run-time if they are loaded.
    if utils.module_imported('mymod'):
        mymod.say_hello()
    else:
        logger.log('*** NOTE: mymod is not imported ***')
    if utils.module_imported('mypackage'):
        mypackmod.say_hello()
    else:
        logger.log('*** NOTE: mypackmod is not imported ***')
