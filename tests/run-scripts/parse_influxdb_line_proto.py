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

import lark

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
        {'fk0': "\\\"this 'is' fine\\\""}
    ]

    for name in good_names:
        for tag in good_tags:
            for field in good_fields:
                measurement = datasink.InfluxDBMeasurement(
                    name,
                    tags=tag,
                    values=field,
                    verify_data=True
                )
                logger.log(f'Parsing GOOD: {measurement.data()}')

    bad_names = [
        '_a_bad_name',
        '.a_bad_name',
        '-a_bad_name'
    ]

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
                    logger.log(f'Parsing BAD NAME: {name}')
                    measurement.data()
                    assert False
                except SyntaxError as exception:
                    logger.log(f'BAD: WHY: {exception}\n')
                except (lark.exceptions.UnexpectedToken,
                        lark.exceptions.UnexpectedCharacters) as exception:
                    logger.log(f'BAD: WHY: {exception}\n')

    bad_tags = [
        None,
        {'_tk0': "tk0"},
        {'tk0': 'tv0:tv1=tv2'}
    ]

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
                    if tag is None:
                        continue
                    logger.log(f'Parsing BAD TAG: {tag}')
                    measurement.data()
                    assert False
                except SyntaxError as exception:
                    logger.log(f'BAD: WHY: {exception}\n')
                except (lark.exceptions.UnexpectedToken,
                        lark.exceptions.UnexpectedCharacters) as exception:
                    logger.log(f'BAD: WHY: {exception}\n')

    bad_fields = [
        {'_fk0': "fv0"},
        {'fk0': 'good', '_fk1': 'bad'}
    ]

    for name in good_names:
        for tag in good_tags:
            for field in bad_fields:
                measurement = datasink.InfluxDBMeasurement(
                    name,
                    tags=tag,
                    values=field,
                    verify_data=True
                )
                try:
                    logger.log(f'Parsing BAD FIELD: {field}')
                    measurement.data()
                    assert False
                except SyntaxError as exception:
                    logger.log(f'BAD: WHY: {exception}\n')
                except (lark.exceptions.UnexpectedToken,
                        lark.exceptions.UnexpectedCharacters) as exception:
                    logger.log(f'BAD: WHY: {exception}\n')

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
        'name fk0=True,fk1=False,fk2=+0.3 1465839830100400200\n',
    ]

    bad_vals = [
        '_name, fk0="fv0" 1465839830100400200\n',
        'name,_fk0="fv0" 1465839830100400200\n',
        'name,_tk0=tv0 fk0="fv0" 1465839830100400200\n',
        'name,tk0=tv0 1465839830100400200\n',
        'name,tk0=tv0 fk0="fv0" \n',
        'name,tk0=tv0:tv1=tv2,tk1=tv1 fk0="fv0" 1465839830100400200\n'
    ]

    parser = datasink._InfluxLineProtocolParser()

    for good in good_vals:
        logger.log(f'Parsing Good: {good}')
        parser.parse(good)

    for bad in bad_vals:
        try:
            logger.log(f'Parsing Bad: {bad}')
            parser.parse(bad)
            assert False
        except SyntaxError as exception:
            logger.log(f'BAD: {bad}WHY: {exception}\n')
        except (lark.exceptions.UnexpectedToken,
                lark.exceptions.UnexpectedCharacters) as exception:
            logger.log(f'BAD: {bad}WHY: {exception}\n')
    logger.log('SUCCESS!')


# vim: ft=python ts=4 sts=4 sw=4 expandtab
