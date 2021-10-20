from bueno.public import experiment
from bueno.public import host
from bueno.public import logger
from bueno.public import metadata

experiment.name('metadata')


def main(argv):
    logger.log('Adding a file asset...')
    # Add an arbitrary metadata file to a subdirectory.
    metadata.add_asset(
        metadata.FileAsset('some-metadata.txt', 'subdir-a/subdir-b')
    )

    logger.log('Adding a YAML dictionary asset...')
    adict = {}
    # Populate the dictionary with relevant metadata.
    adict['Application'] = {'argv': argv}
    adict['System'] = {
        'whoami': host.whoami(),
        'hostname': host.hostname()
    }
    # Save metadata to file.
    metadata.add_asset(metadata.YAMLDictAsset(adict, 'yaml-metadata'))
