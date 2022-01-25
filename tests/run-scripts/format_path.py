#
# Copyright (c) 2020-2022 Triad National Security, LLC
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
    ocache = experiment._TheFOutputCache()
    # Name the experiment.
    experiment.name('format-path-test')

    epath = experiment.foutput()
    path = ocache.path(epath)
    logger.log(f'Encoded Path: {epath} Decoded: {path}')

    epath2 = experiment.foutput()
    path2 = ocache.path(epath)
    logger.log(f'Encoded Path: {epath2} Decoded: {path2}')

    assert (epath == epath2) and (path == path2)

    experiment.name('format-path-test-2')

    epath = experiment.foutput()
    path = ocache.path(epath)
    logger.log(f'Encoded Path: {epath} Decoded: {path}')

    assert (epath == epath2) and (path != path2)

    epath = '/%d/%h/%i/%n/%t/%u'
    path = ocache.path(epath)
    logger.log(f'Encoded Path: {epath} Decoded: {path}')

    epath = epath + epath
    path = ocache.path(epath)
    logger.log(f'Encoded Path: {epath} Decoded: {path}')

    epath = '/tmp'
    path = ocache.path(epath)
    logger.log(f'Encoded Path: {epath} Decoded: {path}')

    experiment.name('format-path-test')
