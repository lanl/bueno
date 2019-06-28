#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Operating system utilities for *nix systems.
'''

from bueno.core import utils
from bueno.core import shell


def kernel():
    '''
    Returns the kernel name.
    '''
    return utils.chomp(shell.capture('uname -s'))


def kernelrel():
    '''
    Returns the kernel release.
    '''
    return utils.chomp(shell.capture('uname -r'))
