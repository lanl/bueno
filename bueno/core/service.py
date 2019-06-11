#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

class Service:
    def __init__(self):
        pass

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
        return sname in ServiceFactory.services

    @staticmethod
    def build(sargv):
        '''
        Imports and returns instance of requested service module.
        '''
        import importlib

        sname = sargv[0]
        if not ServiceFactory.known(sname):
            raise ValueError("'{}': Unrecognized service.".format(sname))
        mod = 'bueno.{}.service'.format(sname)
        service = importlib.import_module(mod)
        return service.impl()
