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

from bueno.build import builder

from bueno.public import logger
from bueno.public import metadata
from bueno.public import shell
from bueno.public import utils

from typing import (
    Any
)

import os


class impl(builder.Base):
    '''
    Implements the CharlieCloud container builder.
    '''
    def __init__(self, **config: Any) -> None:
        super().__init__(**config)
        # The command used to build a container.
        self.buildc = 'ch-build'
        # Use ch-grow for unprivileged container builds.
        self.builder = 'ch-grow'
        # The command used to flatten an image into a tarball.
        self.tarcmd = 'ch-builder2tar'
        # The name of the specification file used to build containers.
        self.spec_name = 'Dockerfile'

        self._spec_fixup()

    def _spec_fixup(self) -> None:
        ospec = self.config['spec']
        basen = os.path.basename(ospec)
        if basen == self.spec_name:
            self.config['spec'] = os.path.dirname(ospec)

    def _check_env(self) -> None:
        '''
        Build environment verification function.

        Raises OSError if the environment is unsatisfactory.
        '''
        logger.emlog('# Checking your build environment...')

        inyp = 'Is it in your PATH?\n'
        notf = "'{}' not found. " + inyp
        errs = str()

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

    def _emit_builder_info(self) -> None:
        '''
        Emits builder information gathered at run-time.
        '''
        binfo = dict()
        binfo['Builder'] = {
            'which':   shell.which(self.buildc),
            'version': shell.capture('{} --version'.format(self.buildc)),
        }

        utils.yamlp(binfo, 'Builder')
        metadata.add_asset(metadata.YAMLDictAsset(binfo, 'builder'))

    def _emit_build_spec(self) -> None:
        dockerf = os.path.join(self.config['spec'], self.spec_name)
        # Add spec file to the metadata assets.
        metadata.add_asset(metadata.FileAsset(dockerf))
        # Emit the contents of the spec file.
        logger.log('# Begin Spec Output')
        logger.log(utils.chomp(str().join(shell.cat(dockerf))))
        logger.log('# End Spec Output')

    def _get_path_to_storage(self) -> str:
        cmd = '{} -b {} -t {} --print-storage {}'.format(
            self.buildc,
            self.builder,
            self.config['tag'],
            self.config['spec']
        )
        cmdo = utils.chomp(shell.capture(cmd))
        # Now do some filtering because the output emits more than just the
        # storage path.
        lst = list(filter(lambda x: 'building with' not in x, cmdo.split('\n')))
        if len(lst) < 1:
            msg = 'Could not determine storage ' \
                  'path from the following output:\n{}'
            raise RuntimeError(msg.format(cmdo))
        # Hope for the best because of the rudimentary filtering used (i.e.,
        # hope lst[0] is a valid path). If this ever becomes problematic,
        # implement something nicer. Also, not a huge deal because the returned
        # value will be used in later file operations (let them fail).
        basep = lst[0]
        # Now build up the entire image path. The convention appears to be:
        # basep/img/tag:latest
        specn = '{}:latest'.format(self.config['tag'])
        return os.path.join(basep, 'img', specn)

    def _add_metadata(self) -> None:
        logger.log('# Adding metadata to container...')
        spath = self._get_path_to_storage()
        logger.log('# Looking for {}'.format(spath))
        if not os.path.exists(spath):
            msg = 'The following path does not exist: {}'.format(spath)
            raise RuntimeError(msg)
        logger.log('# Looks good. Adding metadata...')
        metadata.write(os.path.join(spath, 'bueno'))

    def _flatten(self) -> None:
        tcmd = '{} {} {}'.format(
            self.tarcmd,
            self.config['tag'],
            self.config['output_path']
        )

        logger.log('# Begin Flatten Output')
        os.environ['CH_BUILDER'] = self.builder
        shell.run(tcmd, echo=True)
        logger.log('# End Flatten Output')

    def _build(self) -> None:
        bcmd = '{} -b {} -t {} {}'.format(
            self.buildc,
            self.builder,
            self.config['tag'],
            self.config['spec']
        )

        logger.emlog('# Begin Build Output')
        # Run the command specified by bcmd.
        shell.run(bcmd, echo=True)
        logger.emlog('# End Build Output')

    def start(self) -> None:
        self._check_env()
        self._emit_builder_info()
        self._emit_build_spec()
        self._build()
        self._add_metadata()
        self._flatten()
