#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Core utility module.
'''

import os


def privileged_user() -> bool:
    '''
    Returns whether or not the user is a privileged user.
    '''
    return os.getuid() == 0
