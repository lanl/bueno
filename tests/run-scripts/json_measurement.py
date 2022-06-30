#
# Copyright (c) 2021-2022 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

# pylint: disable=protected-access,too-many-locals,too-many-branches

'''
Test 1 for JSON measurement serialization.
'''

import sys
import json
import datetime

from bueno.public import experiment
from bueno.public import logger
from bueno.public import datasink


def main(_):
    '''
    main()
    '''
    experiment.name('json-measurement')

    good_input = [
        {'a': 'b'},
        {'a': 1},
        {'a': 3.14},
        {'a': {'nest': 1.2}},
        {'a_list': [1, 2, 3]},
        {'b_list': ['a', 'b', 'c']},
        {'c_list': ['"a"', 'b', 'c']},
        {'timestamp': 'foo'},
        {'foo': 'timestamp'}
    ]

    logger.log('# Testing JSON measurement serialization...')
    for ginput in good_input:
        measurement = datasink.JSONMeasurement(ginput)
        try:
            data = measurement.data()
            json.loads(data)
            logger.log(f'GOOD\n{data}')
        except Exception as exception:  # pylint: disable=broad-except
            logger.log(f'{exception}')
            logger.log(f'# FAILED on {ginput}')
            sys.exit(1)

    good_input = [
        {'a': 'b'},
    ]

    logger.log('# Testing JSON measurement serialization with datetime...')
    for ginput in good_input:
        cdate = datetime.datetime(2017, 3, 31)
        measurement = datasink.JSONMeasurement(ginput, cdate.timestamp())
        try:
            data = measurement.data()
            json.loads(data)
            logger.log(f'GOOD\n{data}')
        except Exception as exception:  # pylint: disable=broad-except
            logger.log(f'{exception}')
            logger.log(f'# FAILED on {ginput}')
            sys.exit(1)

    logger.emlog('# Test Passed')

# vim: ft=python ts=4 sts=4 sw=4 expandtab
