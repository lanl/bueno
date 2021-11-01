#
# Copyright (c) 2020-2021 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

# pylint: disable=protected-access

'''
Tests path formatting operations.
'''

from bueno.public import experiment
from bueno.public import logger


def main(_):
    '''
    main()
    '''
    # Name the experiment.
    experiment.name('format-path-test')

    epath = '/%d/%h/%i/%n/%t/%u'
    path = experiment._format_path(epath)
    logger.log(F'Encoded Path: {epath} Decoded: {path}')

    epath = epath + epath
    path = experiment._format_path(epath)
    logger.log(F'Encoded Path: {epath} Decoded: {path}')

    epath = '/tmp'
    path = experiment._format_path(epath)
    logger.log(F'Encoded Path: {epath} Decoded: {path}')
