from bueno.public import experiment
from bueno.public import host
from bueno.public import logger
from bueno.public import data


def main(argv):
    experiment.name('data')

    logger.log('Adding a file asset...')
    # Add an arbitrary data file to a subdirectory.
    data.add_asset(
        data.FileAsset('some-data.txt', 'subdir-a/subdir-b')
    )
    # Flushes data to default path.
    data_opath = experiment.flush_data()
    logger.log(f'- Flushing Data to {data_opath}')

    experiment.name('data-2')
    logger.log('Adding a YAML dictionary asset...')
    adict = {}
    # Populate the dictionary with relevant data.
    adict['Application'] = {'argv': argv}
    adict['System'] = {
        'whoami': host.whoami(),
        'hostname': host.hostname()
    }
    # Save data to file.
    data.add_asset(data.YAMLDictAsset(adict, 'yaml-data'))
    # Write data to a custom sub-directory:
    # %n - Experiment name
    # %u - User
    # %h - Host
    # %d - Date
    # %i - Unique ID in subdirectory
    data_opath = experiment.flush_data('%n/%u/%h/%d/%i')
    logger.log(f'- Flushing Data to {data_opath}')

    # And you can also change where data is written at the end of program
    # termination.
    experiment.foutput('%u/a-subdir/%d/%i')
