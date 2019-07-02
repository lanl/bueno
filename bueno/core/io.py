#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

from __future__ import print_function
import sys


def eprint(*args, **kwargs):
    '''
    Similar to print(), but text is emitted to stderr.
    '''
    print(*args, file=sys.stderr, **kwargs)


def ehorf():
    '''
    Prints to stderr error header or footer.
    '''
    eprint('>>!<<')
