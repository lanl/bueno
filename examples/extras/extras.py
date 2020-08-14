from bueno.public import experiment
from bueno.public import logger
from bueno.public import metadata

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
    # Use the extra modules we specified at run-time
    mymod.say_hello()
    mypackmod.say_hello()
