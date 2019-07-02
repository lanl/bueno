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

import importlib


class Factory:
    '''The builder factory.'''
    # List of supported builder names.
    # Modify this list as container builders change.
    avail = [
        'charliecloud'
    ]

    @staticmethod
    def available():
        '''
        Returns list of available builders.
        '''
        return Factory.avail

    @staticmethod
    def known(sname):
        '''
        Returns a boolean indicating whether or not the provided name is known
        builder.
        '''
        return sname in Factory.avail

    @staticmethod
    def build(cname):
        '''
        Imports and returns an instance of requested builder module.
        '''
        if not Factory.known(cname):
            raise ValueError("'{}': Unrecognized builder.".format(cname))
        # Build the import_module string, following the project's service
        # structure convention. Then feed it to import_module to get the
        # requested builder module.
        imod = 'bueno.build.{}'.format(cname)
        builder = importlib.import_module(imod)
        # Return the builder instance.
        return builder.impl()


class Base(ABC):
    '''
    Abstract base class of all builders.
    '''
    def __init__(self):
        pass

    @abstractmethod
    def start(self):
        '''
        Starts the builder. Akin to a builder main().
        '''
        pass
