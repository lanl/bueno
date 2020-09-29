#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
The CharlieCloud container builder.
'''

from typing import (
    Any
)

import os

from bueno.build import builder

from bueno.core import constants

from bueno.public import host
from bueno.public import logger
from bueno.public import metadata
from bueno.public import utils


class impl(builder.Base):  # pylint: disable=C0103
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

        self._spec_fixup()

    def _spec_fixup(self) -> None:
        # The entire specification. This should be a file, something like
        # /home/user/Dockerfile.custom.
        ospec = self.config['spec']

        if not os.path.isfile(ospec):
            emsg = F'Invalid build specification file provided: {ospec}'
            raise ValueError(emsg)

        self.config['spec'] = os.path.abspath(ospec)

    def _check_env(self) -> None:
        '''
        Build environment verification function.

        Raises OSError if the environment is unsatisfactory.
        '''
        logger.emlog('# Checking your build environment...')

        inyp = 'Is it in your PATH?\n'
        notf = "'{}' not found. " + inyp
        errs = str()

        if not host.which(self.buildc):
            errs += notf.format(self.buildc)

        if not host.which(self.tarcmd):
            errs += notf.format(self.tarcmd)

        if errs:
            raise OSError(utils.chomp(errs))

    def _emit_builder_info(self) -> None:
        '''
        Emits builder information gathered at run-time.
        '''
        binfo = dict()
        binfo['Builder'] = {
            'which':   host.which(self.buildc),
            'version': host.capture('{} --version'.format(self.buildc)),
        }

        utils.yamlp(binfo, 'Builder')
        metadata.add_asset(metadata.YAMLDictAsset(binfo, 'builder'))

    def _emit_build_spec(self) -> None:
        dockerf = self.config['spec']
        # Add spec file to the metadata assets.
        metadata.add_asset(metadata.FileAsset(dockerf))
        # Emit the contents of the spec file.
        logger.log('# Begin Spec Output')
        logger.log(utils.chomp(str().join(utils.cat(dockerf))))
        logger.log('# End Spec Output')

    def _get_path_to_storage(self) -> str:
        cmd = F'{self.builder} storage-path'
        basep = utils.chomp(host.capture(cmd))
        # Now build up the entire image path. The convention appears to be:
        # basep/img/tag
        specn = self.config['tag']
        return os.path.join(basep, 'img', specn)

    def _add_metadata(self) -> None:
        logger.log('# Adding metadata to container...')
        spath = self._get_path_to_storage()
        logger.log('# Looking for {}'.format(spath))
        if not os.path.exists(spath):
            msg = 'The following path does not exist: {}'.format(spath)
            raise RuntimeError(msg)
        logger.log('# Looks good. Adding metadata...')
        metadata.write(os.path.join(spath, constants.METADATA_DIR))

    def _flatten(self) -> None:
        tcmd = '{} {} {}'.format(
            self.tarcmd,
            self.config['tag'],
            self.config['output_path']
        )

        logger.log('# Begin Flatten Output')
        os.environ['CH_BUILDER'] = self.builder
        host.run(tcmd, echo=True)
        logger.log('# End Flatten Output')

    def _build(self) -> None:
        dockerf = self.config['spec']
        context = os.path.dirname(self.config['spec'])

        bcmd = '{} -b {} -t {} -f {} {}'.format(
            self.buildc,
            self.builder,
            self.config['tag'],
            dockerf,
            context
        )

        logger.emlog('# Begin Build Output')
        # Run the command specified by bcmd.
        host.run(bcmd, echo=True)
        logger.emlog('# End Build Output')

    def start(self) -> None:
        self._check_env()
        self._emit_builder_info()
        self._emit_build_spec()
        self._build()
        self._add_metadata()
        self._flatten()

# vim: ft=python ts=4 sts=4 sw=4 expandtab
