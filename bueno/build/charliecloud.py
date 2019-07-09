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
from bueno.core import utils
from bueno.build import builder

import os


class impl(builder.Base):
    '''
    Implements the CharlieCloud container builder.
    '''
    def __init__(self, **config):
        super().__init__(**config)
        # The command used to build a container.
        self.buildc = 'ch-build'
        # Use ch-grow for unprivileged container builds.
        self.builder = 'ch-grow'
        # The command used to flatten an image into a tarball.
        self.tarcmd = 'ch-builder2tar'

    def _check_env(self):
        '''
        Build environment verification function.

        Raises OSError if the environment is unsatisfactory.
        '''
        inyp = 'Is it in your PATH?'
        notf = "'{}' not found. " + inyp
        errs = ''

        print('# Checking your build environment...')

        if not shell.which(self.buildc):
            errs += notf.format(self.buildc)

        if errs:
            raise OSError(errs)

    def _emit_builder_info(self):
        binfo = dict()
        binfo['Builder'] = {
            'which':   shell.which(self.buildc),
            'version': shell.capture('{} --version'.format(self.buildc)),
        }

        print('# Begin Builder Details (YAML)')
        utils.pyaml(binfo)
        print('# End Builder Details (YAML)')

    def _build(self):
        bcmd = '{} -b {} -t {} {}'.format(
            self.buildc,
            self.builder,
            self.config['cname'],
            self.config['spec']
        )
        print('# Begin build output')
        # Run the command specified by bcmd.
        shell.run(bcmd, echo=True)
        print('# End build output')

        tcmd = '{} {} {}'.format(
            self.tarcmd,
            self.config['cname'],
            self.config['output_path']
        )
        print('# Begin flatten output')
        os.environ['CH_BUILDER'] = self.builder
        shell.run(tcmd, echo=True)
        print('# End flatten output')

    def start(self):
        self._check_env()
        self._emit_builder_info()
        self._build()
