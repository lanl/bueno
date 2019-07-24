#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

from bueno.core import logger
from bueno.core import metadata


def main(argv):
    logger.log('adding file asset...')
    metadata.Assets().add(metadata.FileAsset('some-metadata.txt'))
