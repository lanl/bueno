#
# Copyright (c)      2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Constants used across packages and modules.
'''

# The name of the directory used to store metadata.
METADATA_DIR: str = 'bueno'

# The name used to store service logs.
SERVICE_LOG_NAME: str = 'log.txt'

# The magic from https://stackoverflow.com/questions/1711970 makes cmd
# quoting a non-issue. Pretty slick... Notice that this is a slightly
# modified version to meet our needs.
BASH_MAGIC: str = 'bash -c \'${0} ${1+$@}\''

# vim: ft=python ts=4 sts=4 sw=4 expandtab
