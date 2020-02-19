#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
An example illustrating how to execute commands inside a container.
'''

from bueno.public import container
from bueno.public import experiment
from bueno.public import host


def main(argv):
    experiment.name('hello-container')
    container.run('echo "hello from a container!"')
    host.run('echo "hello from the host!"')
