#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
The good stuff typically called by __main__.
'''

from bueno import _version
from bueno.core import service

import os
import sys
import argparse
import traceback


class ArgumentParser:
    '''
    bueno's argument parser.
    '''
    def __init__(self):
        self.argp = argparse.ArgumentParser(
                        description=self._desc(),
                        allow_abbrev=False
                    )

    def _desc(self):
        '''
        Returns the description string for bueno.
        '''
        return 'Utilities for automating reproducible benchmarking.'

    def _addargs(self):
        self.argp.add_argument(
            'command',
            # Consume the remaining arguments for command's use.
            nargs=argparse.REMAINDER,
            help='Specifies the command to run with optional '
                 'command-specific arguments that follow.',
            choices=service.Factory.available()
        )

        self.argp.add_argument(
            '-t', '--traceback',
            help='Provides detailed exception information '
                 'useful for bug reporting and debugging.',
            action='store_true',
            default=False,
            required=False
        )
        self.argp.add_argument(
            '-v', '--version',
            help='Displays version information.',
            action='version',
            version='%(prog)s {}'.format(_version.__version__)
        )

    def parse(self):
        self._addargs()
        pr = self.argp.parse_args()
        # Make sure that a command was supplied.
        if len(pr.command) == 0:
            self.argp.print_help()
            sys.exit(os.EX_USAGE)
        return pr


class Bueno:
    '''
    Implements the bueno service dispatch system.
    '''
    def __init__(self, pargs):
        service.Factory.build(pargs.command).start()

    @staticmethod
    def main(pargs):
        try:
            Bueno(pargs)
        except Exception as e:
            print(e)
            if pargs.traceback:
                traceback.print_exc()
            return os.EX_SOFTWARE
        return os.EX_OK


def main():
    pargs = ArgumentParser().parse()
    return Bueno.main(pargs)
