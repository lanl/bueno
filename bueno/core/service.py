#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Core service infrastructure used by all bueno services.
'''

from abc import ABC, abstractmethod

import argparse
import importlib


class Base(ABC):
    '''
    Abstract base class of all bueno services.
    '''
    def __init__(self, desc, argv):
        super().__init__()
        # A description of the service and what it does.
        self.desc = desc
        # The potentially modified argument vector passed to a service.
        self.argv = argv
        # The name of the service (program).
        self.prog = argv[0]
        # An instance of the ArgumentParser
        self.argp = argparse.ArgumentParser(
                        prog=self.prog,
                        description=self.desc,
                        allow_abbrev=False
                    )
        # The arguments obtained after _parseargs().
        self.args = None
        # Dictionary used to hold service configuration.
        self.confd = dict()
        # Add and parse arguments.
        self._addargs()
        self._parseargs()

    @abstractmethod
    def _addargs(self):
        '''
        Hook that allows concrete instances to add service-specific arguments.
        '''
        pass

    @abstractmethod
    def start(self):
        '''
        Starts the service. Akin to a service main().
        '''
        pass

    def _parseargs(self):
        '''
        Parses the arguments provided in self.argv.
        '''
        # argv[1:] to remove the service name. If present, the parser fails
        # because it doesn't recognize the service name as the program name.
        self.args = self.argp.parse_args(args=self.argv[1:])


class Factory:
    '''The service factory.'''
    # List of supported service names.
    # Modify this list as services change.
    # TODO(skg) Update and use strategy found in cntrimg.py.
    services = [
        'build',
        'run'
    ]

    @staticmethod
    def available():
        '''
        Returns list of available service names.
        '''
        return Factory.services

    @staticmethod
    def known(sname):
        '''
        Returns a boolean indicating whether or not the provided services name
        is known (i.e., recognized) by bueno.
        '''
        return sname in Factory.services

    @staticmethod
    def build(sargv):
        '''
        Imports and returns an instance of requested service module.
        '''
        sname = sargv[0]
        if not Factory.known(sname):
            raise ValueError("'{}': Unrecognized service.".format(sname))
        # Build the import_module string, following the project's service
        # structure convention. Then feed it to import_module to get the
        # requested service module.
        imod = 'bueno.{}.service'.format(sname)
        service = importlib.import_module(imod)
        # Return the service instance.
        return service.impl(sargv)
