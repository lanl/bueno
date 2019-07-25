#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Container utilities.
'''

from bueno.core import cntrimg


def run(cmd):
    cntrimg.Activator().impl().run(cmd)
