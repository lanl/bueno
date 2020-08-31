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

# The bash magic used to execute commands in a sub-shell. No longer that
# magical, but it once was... in an subtlety broken way.
BASH_MAGIC: str = 'bash -c'

# vim: ft=python ts=4 sts=4 sw=4 expandtab
