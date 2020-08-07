from bueno.public import experiment
from bueno.public import logger
from bueno.public import metadata

from mypackage import mypackmod
import mymod

def main(argv):
    experiment.name('hello-extras')
    logger.log('This is an example of how to use extras')
    # Because bueno cannot easily determine what extra stuff was imported at
    # run-time, add the extras by hand to our run's metadata.
    metadata.add_asset(metadata.FileAsset('mymod.py'))
    metadata.add_asset(
        metadata.FileAsset('mypackage/mypackmod.py', 'mypackage')
    )
    # Use the extra modules we specified at run-time
    mymod.say_hello()
    mypackmod.say_hello()
