#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
An example illustrating how to execute commands inside a container.
'''

from bueno.public import container


def main(argv):
    container.run('echo "hello from a container!"')
