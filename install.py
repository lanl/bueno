#!/usr/bin/env python3

#
# Copyright (c)      2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#
# type: ignore

from io import StringIO

import logging
import os
import re
import shutil
import subprocess
import sys


sys.exit("This doesn't work yet. We're working on it...")


################################################################################
################################################################################
def get_minimum_python_vers():
    verline = open('./bueno/_minpyversion.py').read()
    sr = re.search(
        r"^__bueno_minimum_python_version_str__ = ['\']([^'\']*)['\']",
        verline
    )
    if sr:
        return sr.group(1)
    else:
        raise RuntimeError('Cannot determine minimum Python version.')


pyversion = '.'.join(map(str, sys.version_info[0:3]))
minpyvers = get_minimum_python_vers()

if pyversion < minpyvers:
    sys.exit(F'bueno requires Python >= {minpyvers}')
else:
    print(F'# Python {pyversion}')
################################################################################
################################################################################


class Configuration:

    def __init__(self):
        pass

    class Defaults:
        pass


class TheLogger:
    # Default logging level.
    loglvl = logging.INFO
    # The in-memory buffer used to store logged events.
    logsio = StringIO()
    # Setup the root logger first.
    logging.basicConfig(
        # Emit to stdout, not stderr.
        stream=sys.stdout,
        level=loglvl,
        format='%(message)s'
    )
    # Now instantiate the logger used by derived services.
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(logsio))
    logger.setLevel(loglvl)

    @staticmethod
    def log(msg, *args, **kwargs):
        TheLogger.logger.info(msg, *args, **kwargs)


def log(msg, *args, **kwargs):
    TheLogger.log(F'# {msg}', *args, **kwargs)


def status(msg, *args, **kwargs):
    TheLogger.log(F'# --- {msg}', *args, **kwargs)


def err(msg, *args, **kwargs):
    TheLogger.log(F'\n***\nError: {msg}\n***\n', *args, **kwargs)
    raise Exception()


class Installer:
    # Application name.
    app = 'bueno-install'
    # Application version.
    # IMPORTANT: Never change manually, always use bumpversion.
    ver = '0.0.1'

    def __init__(self, config):
        self.config = config

    def install(self):
        log('{} {}\n'.format(Installer.app, Installer.ver))

        self.check_prereqs()
        self.install_bueno()

    def check_prereqs(self):
        log('Checking System Prerequisites')

        progs = ['go']

        for prog in progs:
            status(F'Looking for {prog}')

            wcmd = shutil.which(prog)
            if wcmd is None:
                err(F'Cannot find {prog}')
            else:
                status(F'Found it: {wcmd}')

        log('')

    def install_bueno(self):
        log('Installing bueno')


def main():
    try:
        Installer(Configuration()).install()
    except Exception:
        # import traceback
        # traceback.print_exc()
        return os.EX_SOFTWARE
    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())
