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

import logging
import os
import shutil
import sys

from io import StringIO
from typing import Any

from bueno.core import metacls


def emlog(msg: str, *args: Any, **kwargs: Any) -> None:
    '''
    Logs the provided message to a central logger with emphasis.
    '''
    realmsg = '\n#\n' + msg + '\n#\n'
    _TheLogger().log(realmsg, *args, **kwargs)


def log(msg: str, *args: Any, **kwargs: Any) -> None:
    '''
    Logs the provided message to a central logger.
    '''
    _TheLogger().log(msg, *args, **kwargs)


def write(topath: str) -> None:
    '''
    Writes the current contents of the log to the path provided.
    '''
    _TheLogger().write(topath)


class _TheLogger(metaclass=metacls.Singleton):
    '''
    The central logger singleton used indirectly (via calls to log(), etc.) by
    all bueno services.
    '''
    def __init__(self) -> None:
        # Default logging level.
        self.loglvl = logging.INFO
        # The in-memory buffer used to store logged events.
        self.logsio = StringIO()
        # Setup the root logger first.
        logging.basicConfig(
            # Emit to stdout, not stderr.
            stream=sys.stdout,
            level=self.loglvl,
            format='%(message)s'
        )
        # Now instantiate the logger used by derived services.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(self.logsio))
        self.logger.setLevel(self.loglvl)

    def log(self, msg: str, *args: Any, **kwargs: Any) -> None:
        '''
        A thin wrapper around internal logger's interface.
        '''
        self.logger.info(msg, *args, **kwargs)

    def write(self, topath: str) -> None:
        '''
        Writes the contents of the log to the specified path.
        '''
        # Start from the beginning.
        self.logsio.seek(0)
        try:
            with open(topath, 'w+') as file:
                shutil.copyfileobj(self.logsio, file)
        # Always seek to end when done.
        finally:
            self.logsio.seek(os.SEEK_END)

# vim: ft=python ts=4 sts=4 sw=4 expandtab
