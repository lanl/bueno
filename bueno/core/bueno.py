#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
The good stuff typically called by main().
'''

from bueno.core import service

import sys
import os
import traceback


class Bueno:
    '''
    Implements the bueno service dispatch system.
    '''

    @staticmethod
    def usage():
        '''
        Emits bueno usage information.
        '''
        # TODO(skg)
        u = '\nusage:'
        print(u)
        print('Services Available:')
        for s in service.Factory.available():
            print('- {}'.format(s))
        print()

    def __init__(self):
        self.argc = len(sys.argv)
        self.argv = sys.argv

        self.check_args()

        self.service = service.Factory.build(self.argv[1:])
        self.service.start()

    def check_args(self):
        '''
        Checks top-level arguments passed to the service dispatch system.
        '''
        if self.argc < 2:
            Bueno.usage()
            sys.exit(os.EX_USAGE)

        if self.argv[1] in ['-h', '--help']:
            Bueno.usage()
            sys.exit(os.EX_OK)


def main():
    try:
        Bueno()
    except ValueError as e:
        print(e)
        Bueno.usage()
        return os.EX_USAGE
    except Exception as e:
        print(e)
        traceback.print_exc()
        return os.EX_CONFIG
    return os.EX_OK
