#
# Copyright (c) 2021-2022 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

# pylint: disable=protected-access

'''
Test 1 for InfluxDB line protocol parser.
'''

import time
import sys


from bueno.public import experiment
from bueno.public import logger
from bueno.public import datasink


def main(_):
    '''
    main()
    '''
    experiment.name('parse-influxdb-line-proto')

    good_names = [
        'n',
        '0',
        'name',
        'a.name',
        'a-name',
        'name_foo0',
        '0_name-foo.0'
    ]

    good_tags = [
        None,
        {'0': "tv0"},
        {'a': "tv0"},
        {'tk0': "tv0"},
        {'tk0': "tv0", 'tk1': "00", 'tk2': "tv2_longer.long"}
    ]

    good_fields = [
        {'0': "fv0"},
        {'a': "fv0"},
        {'fk0': "fv0"},
        {'fk0': "fv0 with spaces"},
        {'fk0': "tk0", 'fk1': 0},
        {'fk0': "tk.0", 'fk1': 0.0, 'fk2': -1.23, 'fk3': 1e-08},
        {'fk0': True, 'fk1': False and True},
        {'fk0': "\\\"this 'is' fine\\\""},
        {'a': {'b': 1, 'c': {'d': 'Double Nest'}}, 'e': 10.1}
    ]

    logger.log('# Testing good inputs...')
    for name in good_names:
        for tag in good_tags:
            for field in good_fields:
                measurement = datasink.InfluxDBMeasurement(
                    name,
                    tags=tag,
                    values=field,
                    verify_data=True
                )
                try:
                    data = measurement.data()
                except Exception as exception:  # pylint: disable=broad-except
                    logger.log(f'{exception}')
                    logger.log(f'# FAILED on {data}')
                    measurement = datasink.InfluxDBMeasurement(
                        name,
                        tags=tag,
                        values=field,
                        verify_data=False
                    )
                    logger.log(f'# data = {measurement.data()}')
                    sys.exit(1)

    bad_names = [
        '_a_bad_name',
        '.a_bad_name',
        '-a_bad_name'
    ]

    logger.log('# Testing bad name inputs...')
    for name in bad_names:
        for tag in good_tags:
            for field in good_fields:
                measurement = datasink.InfluxDBMeasurement(
                    name,
                    tags=tag,
                    values=field,
                    verify_data=True
                )
                try:
                    measurement.data()
                    measurement = datasink.InfluxDBMeasurement(
                        name,
                        tags=tag,
                        values=field,
                        verify_data=False
                    )
                    logger.log(f'# BAD DATA GOT THRU in {measurement.data()}')
                    sys.exit(1)
                except Exception:  # pylint: disable=broad-except
                    pass

    bad_tags = [
        {'_tk0': "tk0"},
        {'tk0': 'tv0:tv1=tv2'}
    ]

    logger.log('# Testing bad tag inputs...')
    for name in good_names:
        for tag in bad_tags:
            for field in good_fields:
                measurement = datasink.InfluxDBMeasurement(
                    name,
                    tags=tag,
                    values=field,
                    verify_data=True
                )
                try:
                    measurement.data()
                    measurement = datasink.InfluxDBMeasurement(
                        name,
                        tags=tag,
                        values=field,
                        verify_data=False
                    )
                    logger.log(f'# BAD DATA GOT THRU in {measurement.data()}')
                    sys.exit(1)
                except Exception:  # pylint: disable=broad-except
                    pass

    bad_fields = [
        {'_fk0': "fv0"},
        {'fk0': 'good', '_fk1': 'bad'},
        {'a': {'b': 1, 'c': True}, 'a_c': False}
    ]

    logger.log('# Testing bad field inputs...')
    for name in good_names:
        for tag in good_tags:
            for field in bad_fields:
                try:
                    # This is here because we raise errors in construction
                    measurement = datasink.InfluxDBMeasurement(
                        name,
                        tags=tag,
                        values=field,
                        verify_data=True
                    )
                    measurement.data()
                    measurement = datasink.InfluxDBMeasurement(
                        name,
                        tags=tag,
                        values=field,
                        verify_data=False
                    )
                    logger.log(f'# BAD DATA GOT THRU in {measurement.data()}')
                    sys.exit(1)
                except Exception:  # pylint: disable=broad-except
                    pass

    good_vals = [
        'a_name_foo1 fk0="fv0" 1465839830100400200\n',
        'name fk0="fv0" 1465839830100400200\n',
        'name fk0="fv0" -1465839830100400200\n',
        'name,tk0=tv0 fk0="fv0" 1465839830100400200\n',
        'name,tk0=tv0,tk1=tv1,tk2=tv2 fk0="fv0" 1465839830100400200\n',
        'name fk0="fv0",fk1=0.1 1465839830100400200\n',
        'name fk0="fv0",fk1=-0.1 1465839830100400200\n',
        'name fk0=0.1,fk1=1e-08 1465839830100400200\n',
        'name fk0=0.1,fk1=1e-08,fk2=3,fk3="fv3" 1465839830100400200\n',
        'name fk0=True,fk1=False,fk2=+0.3 1465839830100400200\n'
    ]

    bad_vals = [
        '_name, fk0="fv0" 1465839830100400200\n',
        'name,_fk0="fv0" 1465839830100400200\n',
        'name,_tk0=tv0 fk0="fv0" 1465839830100400200\n',
        'name,tk0=tv0 1465839830100400200\n',
        'name,tk0=tv0 fk0="fv0" \n',
        'name,tk0=tv0:tv1=tv2,tk1=tv1 fk0="fv0" 1465839830100400200\n'
    ]

    logger.log('# Testing good raw inputs...')
    parser = datasink._InfluxLineProtocolParser()

    for good in good_vals:
        try:
            parser.parse(good)
        except Exception as exception:  # pylint: disable=broad-except
            logger.log(f'{exception}')
            logger.log(f'# FAILED on {good}')
            sys.exit(1)

    logger.log('# Testing bad raw inputs...')
    for bad in bad_vals:
        try:
            parser.parse(bad)
            logger.log(f'# BAD DATA GOT THRU in {bad}')
            sys.exit(1)
        except Exception:  # pylint: disable=broad-except
            pass

    logger.emlog('# Test Passed')

# vim: ft=python ts=4 sts=4 sw=4 expandtab
