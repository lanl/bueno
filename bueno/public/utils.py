#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Utilities for good.
'''

from bueno.public import logger

from datetime import datetime

import yaml


def now():
    '''
    Returns the current date and time.
    '''
    return datetime.now()


def nows():
    '''
    Returns a string representation of the current date and time.
    '''
    return now().strftime('%Y-%m-%d %H:%M:%S')


def chomp(s):
    '''
    Returns a string without trailing newline characters.
    '''
    return s.rstrip()


def yamls(d):
    '''
    Returns YAML string from the provided dictionary.
    '''
    return chomp(yaml.dump(d, default_flow_style=False))


def yamlp(d, label=None):
    '''
    Emits YAML output from the provided dictionary.
    '''
    if not emptystr(label):
        logger.log('# Begin {} Configuration (YAML)'.format(label))

    logger.log(yamls(d))

    if not emptystr(label):
        logger.log('# End {} Configuration (YAML)'.format(label))


def ehorf():
    '''
    Returns header/footer string used for error messages.
    '''
    return '\n>>!<<\n'


def emptystr(s):
    '''
    Returns True if the provided string is not empty; False otherwise.
    '''
    return not (s and s.strip())


class Table:
    class Row():
        def __init__(self, data, withrule=False):
            self.data = data
            self.withrule = withrule

    class RowFormatter():
        def __init__(self, mcls):
            self.colpad = 2
            self.mcls = list(map(lambda x: x + self.colpad, mcls))
            self.fmts = str()
            # Generate format string based on max column lengths.
            for l in self.mcls:
                self.fmts += '{{:<{}s}}'.format(l)

        def format(self, row):
            res = str()
            res += self.fmts.format(*row.data)
            if (row.withrule):
                res += '\n' + ('-' * (sum(self.mcls) - self.colpad))
            return res

    def __init__(self):
        self.rows = list()
        self.maxcollens = list()

    def addrow(self, row, withrule=False):
        if (len(self.rows) == 0):
            ncols = len(row)
            self.maxcollens = [0] * ncols

        srow = list(map(str, row))
        maxlens = map(len, srow)

        self.maxcollens = list(map(max, zip(self.maxcollens, maxlens)))
        self.rows.append(Table.Row(srow, withrule))

    def emit(self):
        rf = Table.RowFormatter(self.maxcollens)
        for r in self.rows:
            logger.log(rf.format(r))
