#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
'''

from bueno.core import utils
from bueno.core import shell


class OS:
    '''
    Operating system (OS) queries for *nix systems.
    '''
    @staticmethod
    def processor():
        return shell.capture('uname -p')


class User:
    '''
    User queries.
    '''
    @staticmethod
    def whoami():
        return utils.chomp(shell.capture('whoami'))
