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

import argparse
import os
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
        def __init__(self, option_strings, dest, nargs, **kwargs):
            super().__init__(option_strings, dest, nargs, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            if len(values) == 0:
                help = '{} requires one positional argument (none provided).'
                parser.print_help()
                parser.error(help.format('bueno'))
            setattr(namespace, self.dest, values)

    def parse(self):
        self._addargs()
        pr = self.argp.parse_args()
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
