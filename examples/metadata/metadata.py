from bueno.public import experiment
from bueno.public import host
from bueno.public import logger
from bueno.public import metadata

experiment.name('metadata')


def main(argv):
    logger.log('adding a file asset...')
    # adds an arbitrary metadata file to a subfolder: custom
    metadata.add_asset(metadata.FileAsset('some-metadata.txt', 'custom'))

    logger.log('adding a yaml dict asset...')
    adict = dict()

    # collect metadata
    adict['Application'] = {'argv': argv}
    adict['System'] = {
        'whoami': host.whoami(),
        'hostname': host.hostname()
    }
    # save metadata to file
    metadata.add_asset(metadata.YAMLDictAsset(adict, 'yaml-metadata'))
