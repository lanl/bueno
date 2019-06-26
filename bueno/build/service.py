#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
The build service module.
'''

from bueno.core import service
from bueno.core import shell

import os


class impl(service.Service):
    '''
    Implements the build service.
    '''
    def __init__(self, argv):
        try:
            super().__init__(argv)
            shell.run('ls -ltrah')
            shell.run('echo hi')
            shell.run('echo $PATH')
            sav = os.environ['PATH']

            os.environ['PATH'] = '/bin'
            shell.run('echo $PATH')

            shell.run('sleep 3')

            os.environ['PATH'] = sav
            shell.run('echo $PATH')

            shell.run('foo')
        except ChildProcessError as e:
            print(e.strerror)

    def start(self):
        pass

    def help(self):
        pass
