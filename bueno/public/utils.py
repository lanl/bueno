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

from bueno.public import logger

from datetime import datetime
from typing import (
    Any,
    List,
    Union
)

import yaml


def cat(file: str) -> List[str]:
    '''
    Akin to cat(1), but returns a list of strings containing the contents of the
    provided file.

    Raises OSError or IOError on error.
    '''
    lines: List[str] = list()

    with open(file, 'r') as file:  # type: ignore
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


def chomp(s: str) -> str:
    '''
    Returns a string without trailing newline characters.
    '''
    return s.rstrip()


def yamls(d: Any) -> str:
    '''
    Returns YAML string from the provided dictionary.
    '''
    return chomp(yaml.dump(d, default_flow_style=False))


def yamlp(d: Any, label: Union[None, str] = None) -> None:
    '''
    Emits YAML output from the provided dictionary.
    '''
    if not emptystr(label):
        logger.log(F'# Begin {label} Configuration (YAML)')

    logger.log(yamls(d))

    if not emptystr(label):
        logger.log(F'# End {label} Configuration (YAML)')


def ehorf() -> str:
    '''
    Returns header/footer string used for error messages.
    '''
    return '\n>>!<<\n'


def emptystr(s: Union[str, None]) -> bool:
    '''
    Returns True if the provided string is not empty; False otherwise.
    '''
    return not (s and s.strip())


class Table:
    class Row():
        def __init__(self, data: List[Any], withrule: bool = False) -> None:
            self.data = data
            self.withrule = withrule

    class RowFormatter():
        def __init__(self, mcls: List[int]) -> None:
            self.colpad = 2
            self.mcls = list(map(lambda x: x + self.colpad, mcls))
            self.fmts = str()
            # Generate format string based on max column lengths.
            for l in self.mcls:
                self.fmts += F'{{:<{l}s}}'

        def format(self, row: 'Table.Row') -> str:
            res = str()
            res += self.fmts.format(*row.data)
            if (row.withrule):
                res += '\n' + ('-' * (sum(self.mcls) - self.colpad))
            return res

    def __init__(self) -> None:
        self.rows: List[Any] = list()
        self.maxcollens: List[Any] = list()

    def addrow(self, row: List[Any], withrule: bool = False) -> None:
        if (len(self.rows) == 0):
            ncols = len(row)
            self.maxcollens = [0] * ncols

        srow = list(map(str, row))
        maxlens = map(len, srow)

        self.maxcollens = list(map(max, zip(self.maxcollens, maxlens)))
        self.rows.append(Table.Row(srow, withrule))

    def emit(self) -> None:
        rf = Table.RowFormatter(self.maxcollens)
        for r in self.rows:
            logger.log(rf.format(r))
