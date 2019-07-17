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
from bueno.core import logger
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
        # The name of the specification file used to build containers.
        self.spec_name = 'Dockerfile'

    def _check_env(self):
        '''
        Build environment verification function.

        Raises OSError if the environment is unsatisfactory.
        '''
        logger.log('# Checking your build environment...')

        inyp = 'Is it in your PATH?\n'
        notf = "'{}' not found. " + inyp
        errs = ''

        if not shell.which(self.buildc):
            errs += notf.format(self.buildc)

        if not shell.which(self.tarcmd):
            errs += notf.format(self.tarcmd)

        # Make sure that a Dockerfile exists in the provided path.
        fixs = 'Please update your specification path.\n'
        dnotf = '{} does not exist. ' + fixs
        dockerf = os.path.join(self.config['spec'], self.spec_name)

        if not os.path.exists(dockerf):
            errs += dnotf.format(dockerf)

        if errs:
            raise OSError(utils.chomp(errs))

    def _emit_builder_info(self):
        '''
        Emits builder information gathered at run-time.
        '''
        binfo = dict()
        binfo['Builder'] = {
            'which':   shell.which(self.buildc),
            'version': shell.capture('{} --version'.format(self.buildc)),
        }

        logger.log('# Begin Builder Details (YAML)')
        utils.pyaml(binfo)
        logger.log('# End Builder Details (YAML)')

    def _build(self):
        bcmd = '{} -b {} -t {} {}'.format(
            self.buildc,
            self.builder,
            self.config['tag'],
            self.config['spec']
        )
        logger.log('# Begin build output')
        # Run the command specified by bcmd.
        shell.run(bcmd, echo=True)
        logger.log('# End build output')

        tcmd = '{} {} {}'.format(
            self.tarcmd,
            self.config['tag'],
            self.config['output_path']
        )
        logger.log('# Begin flatten output')
        os.environ['CH_BUILDER'] = self.builder
        shell.run(tcmd, echo=True)
        logger.log('# End flatten output')

    def start(self):
        self._check_env()
        self._emit_builder_info()
        self._build()
