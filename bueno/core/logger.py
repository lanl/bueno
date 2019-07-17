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
import shutil
import logging
import os


def log(msg, *args, **kwargs):
    '''
    Used to log all service activities.
    '''
    _TheLogger().log(msg, *args, **kwargs)

def save(to):
    '''
    Writes the current contents of the log to the path provided.
    '''
    _TheLogger().save(to)


class _TheLogger(metaclass=metacls.Singleton):
    '''
    The logger singleton used indirectly (via calls to log(), etc.) by all bueno
    services.
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

    def save(self, to):
        # Start from the beginning.
        self.logsio.seek(0)
        try:
            with open(to, 'w+') as f:
                shutil.copyfileobj(self.logsio, f)
        except (OSError, IOError) as e:
            raise(e)
        # Done, so seek back to end.
        finally:
            self.logsio.seek(os.SEEK_END)
