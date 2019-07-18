#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Stores build metadata.
'''

from bueno.core import utils
from bueno.core import logger

import os


def add(basep):
    _MetaData(basep).add()


class _MetaData:
    def __init__(self, basep):
        self.basep = basep
        self.metad = os.path.join(basep, 'bueno')
        self.buildo = 'build-output.txt'

        self._mkdir()

    def add(self):
        logger.log('# Done {}'.format(utils.nows()))
        logger.save(os.path.join(self.metad, self.buildo))

    def _mkdir(self):
        os.makedirs(self.metad, 0o755)
