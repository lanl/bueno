#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

from bueno.public import opsys
from bueno.public import logger
from bueno.public import metadata


def main(argv):
    logger.log('adding a file asset...')
    metadata.add_asset(metadata.FileAsset('some-metadata.txt'))

    logger.log('adding a yaml dict asset...')
    adict = dict()
    adict['Application'] = {'argv': argv}
    adict['System'] = {
        'whoami': opsys.whoami(),
        'hostname': opsys.hostname()
    }
    metadata.add_asset(metadata.YAMLDictAsset(adict, 'yaml-metadata'))
