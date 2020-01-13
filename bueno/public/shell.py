#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Quasi shell-like utilities.
'''

# The magic from https://stackoverflow.com/questions/1711970 makes cmd
# quoting a non-issue. Pretty slick... Notice that this is a slightly
# modified version to meet our needs.
bashmagic = 'bash -c \'${0} ${1+$@}\''
