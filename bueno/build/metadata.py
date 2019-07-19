#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Stores build metadata and provides metadata asset types.
'''

from bueno.core import metadata

import os


def write(basep):
    '''
    Adds build metadata rooted at basep.
    '''
    _MetaData(basep).write()


class _MetaData:
    def __init__(self, basep):
        self.basep = basep
        # The base path where all metadata are stored.
        self.metad = os.path.join(basep, 'bueno')

        os.makedirs(self.metad, 0o755)

    def write(self):
        self._add_default_assets()
        metadata.Assets().deposit(self.metad)

    def _add_default_assets(self):
        metadata.Assets().add(metadata.LoggerAsset())
