from bueno.public import experiment
from bueno.public import host
from bueno.public import logger
from bueno.public import metadata

experiment.name('metadata')


def main(argv):
    logger.log('adding a file asset...')
    metadata.add_asset(metadata.FileAsset('some-metadata.txt'))

    logger.log('adding a yaml dict asset...')
    adict = dict()
    adict['Application'] = {'argv': argv}
    adict['System'] = {
        'whoami': host.whoami(),
        'hostname': host.hostname()
    }
    metadata.add_asset(metadata.YAMLDictAsset(adict, 'yaml-metadata'))
