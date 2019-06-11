#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

import importlib

class Service:
    def __init__(self):
        pass

class ServiceFactory:
    # Supported service names.
    services = [
        'build'
    ]

    @staticmethod
    def available():
        return ServiceFactory.services

    @staticmethod
    def known(sname):
        return sname in ServiceFactory.services


    @staticmethod
    def build(sargv):
        sname = sargv[0]
        if not ServiceFactory.known(sname):
            raise ValueError("'{}': unrecognized service.".format(sname))
        # Import and return requested service module.
        mod = 'bueno.{}.service'.format(sname)
        return importlib.import_module(mod)
