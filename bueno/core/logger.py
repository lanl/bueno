#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Logging utilities for good.
'''

from bueno.core import metacls

from io import StringIO
import logging


def log(msg, *args, **kwargs):
    '''
    Used to log all service activities.
    '''
    _TheLogger().log(msg, *args, **kwargs)


class _TheLogger(metaclass=metacls.Singleton):
    '''
    The logger singleton used by all bueno services.
    '''
    def __init__(self):
        # Default logging level.
        self.loglvl = logging.INFO
        # The in-memory buffer used to store logged events.
        self.logsio = StringIO()
        # Setup the root logger first.
        logging.basicConfig(
            level=self.loglvl,
            format='%(message)s',
        )
        # Now instantiate the logger used by derived services.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(self.logsio))
        self.logger.setLevel(self.loglvl)

    def log(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
