# bueno provides a collection of public modules containing helpful utilities. At
# a minimum, the experiment module contained within the bueno.public package
# must be imported by a bueno run script.
from bueno.public import experiment
from bueno.public import logger

# All bueno experiments must be named. This particular experiment is named
# hello-world.
experiment.name('hello-world')


# main() is the entry point for all bueno run scripts. argv is a list of
# argument strings passed to this program by the bueno run service.
def main(argv):
    # The logger emits strings to the console. Additionally, the output
    # produced by logging actions is recorded and stored in experiment metadata
    # written (by default) after experiment termination.
    logger.log('hello world')
