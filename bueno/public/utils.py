#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Utilities for good.
'''

from datetime import datetime

from typing import (
    Any,
    IO,
    Iterable,
    List,
    Union
)

import sys
import yaml

from bueno.public import logger


def module_imported(modname: str) -> bool:
    '''
    Returns whether or not the provided module name has already been imported.
    '''
    return modname in sys.modules


def cat(filep: str) -> List[str]:
    '''
    Akin to cat(1), but returns a list of strings containing the contents of the
    provided file.

    Raises OSError or IOError on error.
    '''
    lines: List[str] = list()

    with open(filep, 'r') as file:
        for line in file:
            lines.append(line)

    return lines


def cats(file: str) -> str:
    '''
    Akin to cat(1), but returns a string containing the contents of the provided
    file.

    Raises OSError or IOError on error.
    '''
    return str().join(cat(file))


def now() -> datetime:
    '''
    Returns the current date and time.
    '''
    return datetime.now()


def nows() -> str:
    '''
    Returns a string representation of the current date and time.
    '''
    return now().strftime('%Y-%m-%d %H:%M:%S')


def dates() -> str:
    '''
    Returns a string representation of the current date.
    '''
    return now().strftime('%Y-%m-%d')


def chomp(istr: str) -> str:
    '''
    Returns a string without trailing newline characters.
    '''
    return istr.rstrip()


def yamls(idict: Any) -> str:
    '''
    Returns YAML string from the provided dictionary.
    '''
    return chomp(yaml.dump(idict, default_flow_style=False))


def yamlp(idict: Any, label: Union[None, str] = None) -> None:
    '''
    Emits YAML output from the provided dictionary.
    '''
    if not emptystr(label):
        logger.log(F'# Begin {label} Configuration (YAML)')

    logger.log(yamls(idict))

    if not emptystr(label):
        logger.log(F'# End {label} Configuration (YAML)')


def ehorf() -> str:
    '''
    Returns header/footer string used for error messages.
    '''
    return '\n>>!<<\n'


def emptystr(istr: Union[str, None]) -> bool:
    '''
    Returns True if the provided string is not empty; False otherwise.
    '''
    return not (istr and istr.strip())


def read_logical_lines(fileobj: IO[str]) -> Iterable[str]:
    '''
    Reads the contents of fileobj and returns its lines, properly handling line
    continuations.
    '''
    logical_line = []
    for physical_line in fileobj:
        if physical_line.endswith('\\\n'):
            logical_line.append(physical_line[:-2])
        else:
            yield ''.join(logical_line)+physical_line
            logical_line = []
    if logical_line:
        yield ''.join(logical_line)


class Table:
    '''
    A straightforward class to display formatted tabular data.
    '''
    class Row():
        '''
        Creates a row for use in a table.
        '''
        def __init__(self, data: List[Any], withrule: bool = False) -> None:
            self.data = data
            self.withrule = withrule

    class _RowFormatter():
        '''
        Private class used for row formatting.
        '''
        def __init__(self, mcls: List[int]) -> None:
            self.colpad = 2
            self.mcls = list(map(lambda x: x + self.colpad, mcls))
            self.fmts = str()
            # Generate format string based on max column lengths.
            for mcl in self.mcls:
                self.fmts += F'{{:<{mcl}s}}'

        def format(self, row: 'Table.Row') -> str:
            '''
            Formats the contents of a given row into a nice output string.
            '''
            res = str()
            res += self.fmts.format(*row.data)
            if row.withrule:
                res += '\n' + ('-' * (sum(self.mcls) - self.colpad))
            return res

    def __init__(self) -> None:
        self.rows: List[Any] = list()
        self.maxcollens: List[Any] = list()

    def addrow(self, row: List[Any], withrule: bool = False) -> None:
        '''
        Adds the contents of row to a table, optionally with a rule.
        '''
        if len(self.rows) == 0:
            ncols = len(row)
            self.maxcollens = [0] * ncols

        srow = list(map(str, row))
        maxlens = map(len, srow)

        self.maxcollens = list(map(max, zip(self.maxcollens, maxlens)))
        self.rows.append(Table.Row(srow, withrule))

    def emit(self) -> None:
        '''
        Emits the contents of the table using logger.log().
        '''
        rowf = Table._RowFormatter(self.maxcollens)
        for row in self.rows:
            logger.log(rowf.format(row))

# vim: ft=python ts=4 sts=4 sw=4 expandtab
