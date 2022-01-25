#
# Copyright (c) 2020-2022 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

# pylint: disable=protected-access

'''
Tests path formatting operations.
'''

from bueno.public import experiment
from bueno.public import data
from bueno.public import logger


def main(argv):
    '''
    main()
    '''
    ocache = experiment._TheFOutputCache()
    # Name the experiment.
    experiment.name('dataflush')

    epath = str(experiment.foutput())
    path = ocache.path(epath)
    logger.log(f'Encoded Path: {epath} Decoded: {path}')

    adict = {
        'Application': {'argv': argv}
    }
    data.add_asset(data.YAMLDictAsset(adict, 'yaml-data'))

    output = experiment.flush_data()
    assert output.startswith('/dev/null')

    data.add_asset(data.YAMLDictAsset(adict, 'more-yaml-data'))

    output = experiment.flush_data()
    assert output.startswith('/dev/null')

    experiment.name('dataflush-2')
