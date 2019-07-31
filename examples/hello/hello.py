#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

from bueno.public import logger
from bueno.public import experiment

experiment.name('hello')


def main(argv):
    logger.log('hello world')
