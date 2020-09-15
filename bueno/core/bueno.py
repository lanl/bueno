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

import argparse
import os
import sys
import traceback
import typing

from bueno import _version

from bueno.core import service
from bueno.core import utils


class ArgumentParser:
    '''
    bueno's argument parser.
    '''
    def __init__(self) -> None:
        self.argp = argparse.ArgumentParser(
            description=ArgumentParser._desc(),
            allow_abbrev=False
        )

    @staticmethod
    def _desc() -> str:
        '''
        Returns the description string for bueno.
        '''
        return 'Utilities for automating reproducible benchmarking.'

    def _addargs(self) -> None:
        self.argp.add_argument(
            '-t', '--traceback',
            help='Provides detailed exception information '
                 'useful for bug reporting and script debugging.',
            action='store_true',
            default=False,
            required=False
        )
        self.argp.add_argument(
            '-v', '--version',
            help='Displays version information.',
            action='version',
            version=F'%(prog)s {_version.__version__}'
        )
        self.argp.add_argument(
            'command',
            # Consume the remaining arguments for command's use.
            nargs=argparse.REMAINDER,
            help='Specifies the command to run '
                 'followed by command-specific arguments.',
            choices=service.Factory.available(),
            action=ArgumentParser.CommandAction
        )

    class CommandAction(argparse.Action):
        '''
        Custom action class used for 'command' argument structure verification.
        '''
        @typing.no_type_check
        def __init__(self, option_strings, dest, nargs, **kwargs):
            super().__init__(option_strings, dest, nargs, **kwargs)

        @typing.no_type_check
        def __call__(self, parser, namespace, values, option_string=None):
            if len(values) == 0:
                helps = '{} requires one positional argument (none provided).'
                parser.print_help()
                parser.error(helps.format('bueno'))
            setattr(namespace, self.dest, values)

    def parse(self) -> argparse.Namespace:
        '''
        Parses and returns an argparse.Namespace.
        '''
        self._addargs()
        return self.argp.parse_args()


class Bueno:
    '''
    Implements the bueno service dispatch system.
    '''
    def __init__(self, pargs: argparse.Namespace) -> None:
        service.Factory.build(pargs.command).start()

    @staticmethod
    def main(pargs: argparse.Namespace) -> int:
        '''
        Instantiates and runs a bueno service.
        '''
        try:
            Bueno(pargs)
        except Exception as exptn:  # pylint: disable=W0703
            print(exptn)
            if pargs.traceback:
                traceback.print_exc()
            return os.EX_SOFTWARE
        return os.EX_OK


def main() -> int:
    '''
    bueno's main().
    '''
    if utils.privileged_user():
        ers = '\nRunning this program as root is a bad idea... Exiting now.\n'
        sys.exit(ers)

    return Bueno.main(ArgumentParser().parse())

# vim: ft=python ts=4 sts=4 sw=4 expandtab
