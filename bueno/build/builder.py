#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Builders for good.
'''

from abc import ABC, abstractmethod

from typing import (
    Any,
    List
)

import importlib


class Base(ABC):  # pylint: disable=R0903
    '''
    Abstract base class of all builders.
    '''
    def __init__(self, **config: Any) -> None:
        self.config = config

        super().__init__()

    @abstractmethod
    def start(self) -> None:
        '''
        Starts the builder. Akin to a builder main().
        '''


class Factory:
    '''The builder factory.'''
    # List of supported builder names.
    # Modify this list as container builders change.
    avail = [
        'charliecloud'
    ]

    @staticmethod
    def available() -> List[str]:
        '''
        Returns list of available builders.
        '''
        return Factory.avail

    @staticmethod
    def known(sname: str) -> bool:
        '''
        Returns a boolean indicating whether or not the provided name is a known
        builder.
        '''
        return sname in Factory.avail

    @staticmethod
    def build(**config: Any) -> Any:
        '''
        Imports and returns an instance of requested builder module.
        '''
        builder = config['builder']
        if not Factory.known(builder):
            raise ValueError("'{}': Unrecognized builder.".format(builder))
        # Build the import_module string, following the project's service
        # structure convention. Then feed it to import_module to get the
        # requested builder module.
        imod = 'bueno.build.{}'.format(builder)
        builder = importlib.import_module(imod)
        # Return the builder instance.
        return builder.impl(**config)

# vim: ft=python ts=4 sts=4 sw=4 expandtab
