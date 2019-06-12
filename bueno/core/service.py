#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Core services.
'''

from abc import ABC, abstractmethod


class Service(ABC):
    '''
    Abstract base class of all bueno services.
    '''
    def __init__(self, argv):
        self.argv = argv
        super(Service, self).__init__()

    @abstractmethod
    def help(self):
        pass

    @abstractmethod
    def start(self):
        pass


class ServiceFactory:
    '''The service factory.'''
    # List of supported service names.
    # Modify this list as services change.
    services = [
        'build',
        'run'
    ]

    @staticmethod
    def available():
        '''
        Returns list of available service names.
        '''
        return ServiceFactory.services

    @staticmethod
    def known(sname):
        '''
        Returns a boolean indicating whether or not the provided services name
        is known (i.e., recognized) by bueno.
        '''
        return sname in ServiceFactory.services

    @staticmethod
    def build(sargv):
        '''
        Imports and returns an instance of requested service module.
        '''
        import importlib

        sname = sargv[0]
        if not ServiceFactory.known(sname):
            raise ValueError("'{}': Unrecognized service.".format(sname))
        # Build the import_module string, following the project's service
        # structure convention. Then feed it to import_module to get the
        # requested service module.
        imod = 'bueno.{}.service'.format(sname)
        service = importlib.import_module(imod)
        # Return the service instance.
        return service.impl(sargv)
