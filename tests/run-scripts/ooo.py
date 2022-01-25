#
# Copyright (c) 2020-2022 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Tests order of operations.
'''

from bueno.core import mathex

from bueno.public import experiment
from bueno.public import logger


def main(_):
    '''
    main()
    '''
    # Name the experiment.
    experiment.name('ooo-test')

    exprs = [
        '4 / 3 * 2 - 1 + 0',
        '-1 - -2 - -3',
        '-(1 - 2) - (3 - 4)',
        '((1 / 2) * (3 * 4))',
        '((1 / 2) * (3 * 4)) - 5 / 6 * 7**8',
        '((1 / 2) * (3 * 4)) - 5 / 6 * 7**8 % 9',
        '(10 % 9) % 8 - 7 * 6 + 5 % (4)',
        '0**0',
        '0**1',
        '1**0',
        '-10**2',
        '-(10)**-2',
        '-1**2-3',
        '2**(3**4)',
        '(2**3)**4',
        '2**3**4',
        '-1**2**-3**4 * 5',
        '1+1+-1+3'
    ]

    for i in exprs:
        logger.log(f'# Testing {i}')
        pyans = int(eval(i))
        means = mathex.evaluate(i)
        logger.log(f'# Python says the answer is {pyans}')
        logger.log(f'# Mathex says the answer is {means}')
        # Our goal is consistency with Python.
        if pyans != means:
            raise ValueError(f'{pyans} != {means}')
        logger.log('')
