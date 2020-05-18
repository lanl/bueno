#
# Copyright (c)      2020 Triad National Security, LLC
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


def main(argv):
    # Name the experiment.
    experiment.name('ooo')

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
        '-1**2**-3**4 * 5'
    ]

    for i in exprs:
        logger.log(F'# Testing {i}')
        pa = int(eval(i))
        me = mathex.evaluate(i)
        logger.log(F'# Python says the answer is {pa}')
        logger.log(F'# Mathex says the answer is {me}')
        # Our goal is consistency with Python.
        assert(pa == me)
        logger.log('')
