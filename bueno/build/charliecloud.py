#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
The CharlieCloud container builder.
'''

from bueno.core import shell
from bueno.build import builder


class impl(builder.Base):
    '''
    Implements the CharlieCloud container builder.
    '''

    def __init__(self):
        super().__init__()
        self.name = "CharlieCloud"
        # The command used to build a container.
        self.buildc = 'ch-build'
        # Use ch-grow for unprivileged container builds.
        self.builder = 'ch-grow'

    def _sane_env(self):
        '''
        Build environment verification function.

        Raises OSError if the environment is unsatisfactory.
        '''
        inyp = 'Is it in your PATH?'
        notf = "'{}' not found. " + inyp
        errs = ''

        print('# Checking your build environment...')

        if shell.which(self.buildc) is None:
            errs += notf.format(self.buildc)

        if errs:
            raise OSError(errs)

    def _build(self):
        vers = shell.capture('{} --version'.format(self.buildc))
        print('# Starting {} {} build...'.format(self.name, vers))

        bcmd = '{} -b {} -t TODO .'.format(self.buildc, self.builder)
        print('# $ {}'.format(bcmd))
        shell.run(bcmd)

    def start(self, **kwargs):
        self._sane_env()
        self._build()
