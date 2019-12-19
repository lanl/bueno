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

from bueno.public import shell
from bueno.public import utils


def kernel() -> str:
    '''
    Returns the kernel name.
    '''
    return shell.capture('uname -s')


def kernelrel() -> str:
    '''
    Returns the kernel release.
    '''
    return shell.capture('uname -r')


def hostname() -> str:
    '''
    Returns the host computer's name.
    '''
    return shell.capture('hostname')


def whoami() -> str:
    '''
    Akin to whoami(1).
    '''
    return shell.capture('whoami')


def pretty_name() -> str:
    '''
    Returns the host's pretty name as reported by /etc/os-release.
    '''
    name = 'Unknown'
    try:
        with open('/etc/os-release') as osrel:
            for line in osrel:
                if not line.startswith('PRETTY_NAME='):
                    continue
                else:
                    name = utils.chomp(line.split('=')[1]).strip('"')
                    break
    except (OSError, IOError):
        pass

    return name
