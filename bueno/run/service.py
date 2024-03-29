#
# Copyright (c) 2019-2022 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
The run service module.
'''

import argparse
import copy
import importlib.util
import os
import sys
import tarfile
import typing

from typing import (
    List
)

from bueno.core import cntrimg
from bueno.core import constants
from bueno.core import service

from bueno.public import container
from bueno.public import experiment
from bueno.public import host
from bueno.public import logger
from bueno.public import data
from bueno.public import utils


class _Runner:
    @typing.no_type_check
    @staticmethod
    def run(argv: List[str]) -> None:
        '''
        Loads and executes the run program specified at argv[0], passing along
        all program-specific arguments to the program (argv).
        '''
        argz = argv[0]
        # Stash the program.
        data.add_asset(data.FileAsset(argz))
        # Import and run the specified program. argz passed twice for nicer
        # error messages when a user specifies a bogus program.
        spec = importlib.util.spec_from_file_location(argz, argz)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main(argv)


class _ImageStager():
    '''
    Implements the container image stager.
    '''
    def __init__(self) -> None:
        self.basep = host.tmpdir()

    @staticmethod
    def prun_generate() -> str:
        '''
        Returns the command string used for parallel launches.
        '''
        return container.ImageStager().staging_cmd_hook()

    @staticmethod
    def get_img_dir_name(imgp: str) -> str:
        '''
        Returns the expected path for the container image directory given a path
        to an image tarball. Raises ValueError if an exception occurs.
        '''
        # List of common tarball file extensions.
        tfex = ['.tar.gz', '.tgz']
        fname = os.path.basename(imgp)

        fex = [x for x in tfex if fname.endswith(x)]
        if not fex:
            raise ValueError(f'{fname} does not end in any of {tfex}.'
                             'Cannot determine target destination after '
                             'container image staging.')
        # Return the file name without whatever file extension it once had.
        return fname[:-len(fex[0])]

    def stage(self, imgp: str) -> str:
        '''
        Stages the provided container image to an instance-determined base
        directory. The staged image path is returned if the staging completed
        successfully.
        '''
        stage_cmd = f'{_ImageStager.prun_generate()} ' \
                    f'{cntrimg.activator().tar2dirs(imgp, self.basep)}'
        runargs = {
            'echo': True,
            'verbose': False
        }
        host.run(stage_cmd, **runargs)
        return os.path.join(self.basep, _ImageStager.get_img_dir_name(imgp))


class impl(service.Base):  # pylint: disable=invalid-name
    '''
    Implements the run service.
    '''
    class _defaults:
        '''
        Convenience container for run service defaults.
        '''
        desc = 'The run service runs programs and can serve ' \
               'as a dispatch service to container activators.'
        # Path to save any generated files.
        output_path = os.getcwd()
        # The image activator to use by default.
        imgactvtr = 'charliecloud'
        # The image path.
        image = None
        # Whether or not to skip container image staging.
        do_not_stage = False

    class ProgramAction(argparse.Action):
        '''
        Custom action class used for 'program' argument structure verification.
        '''
        @typing.no_type_check
        def __init__(self, option_strings, dest, nargs, **kwargs):
            super().__init__(option_strings, dest, nargs, **kwargs)

        @typing.no_type_check
        def __call__(self, parser, namespace, values, option_string=None):
            if len(values) == 0:
                helps = f'{option_string} requires at least one ' \
                        'argument (none provided).\nPlease provide ' \
                        'a path to the program you wish to run, ' \
                        'optionally followed by program-specific arguments.'
                parser.error(helps)
            # Capture and update values[0] to an absolute path.
            prog = values[0] = os.path.abspath(values[0])
            if not os.path.isfile(prog):
                estr = f'{prog} is not a file. Cannot continue.'
                parser.error(estr)
            setattr(namespace, self.dest, values)

    class ImageAction(argparse.Action):
        '''
        Custom action class used for 'image' argument handling.
        '''
        @typing.no_type_check
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            super().__init__(option_strings, dest, **kwargs)

        @typing.no_type_check
        def __call__(self, parser, namespace, values, option_string=None):
            imgp = os.path.abspath(values)
            if not os.path.exists(imgp):
                estr = f'Cannot access {imgp}'
                parser.error(estr)
            setattr(namespace, self.dest, imgp)

    class ImageActivatorAction(argparse.Action):
        '''
        Custom action class used for 'image-activator' argument handling.
        '''
        @typing.no_type_check
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            # Store reference to imgdir_arg for later use.
            self.imgdir_arg = kwargs.pop('imgdir_arg')
            super().__init__(option_strings, dest, **kwargs)

        @typing.no_type_check
        def __call__(self, parser, namespace, values, option_string=None):
            # Adjust image options if the image activator is none.
            if values == 'none':
                self.imgdir_arg.required = False
                self.imgdir_arg.help = argparse.SUPPRESS
            setattr(namespace, self.dest, values)

    class ExtrasAction(argparse.Action):
        '''
        Custom action class used for 'extras' argument handling.
        '''
        @typing.no_type_check
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            super().__init__(option_strings, dest, **kwargs)

        @typing.no_type_check
        def __call__(self, parser, namespace, values, option_string=None):
            paths = values.split(':')
            for path in paths:
                modpath = os.path.abspath(path)
                if not os.path.exists(modpath):
                    estr = f'Cannot access {modpath}'
                    parser.error(estr)
                if not os.path.isdir(modpath):
                    estr = 'Cannot provide regular ' \
                           f'files to {self.dest}: {path}'
                    parser.error(estr)
                sys.path.append(rf'{modpath}')
            setattr(namespace, self.dest, values)

    def __init__(self, argv: List[str]) -> None:
        super().__init__(impl._defaults.desc, argv)
        # Path to the inflated container image used for activation.
        self.inflated_cntrimg_path = ''

    def _addargs(self) -> None:
        self.argp.add_argument(
            '-o', '--output-path',
            type=str,
            help='Specifies the base output directory used for all '
                 'generated files. To suppress output set to /dev/null. '
                 'Default: PWD',
            default=impl._defaults.output_path,
            required=False,
            metavar='PATH'
        )

        self.argp.add_argument(
            '--do-not-stage',
            action='store_true',
            help='Turns off container image staging when present.',
            default=impl._defaults.do_not_stage,
            required=False
        )

        imgdir_arg = self.argp.add_argument(
            '-i', '--image',
            type=str,
            help='Specifies the base container image tarball or directory.',
            required=True,
            default=impl._defaults.image,
            action=impl.ImageAction
        )

        # Must be located after definition of imgdir_arg because we pass it to
        # ImageActivatorAction
        self.argp.add_argument(
            '-a', '--image-activator',
            type=str,
            help=f'Specifies the image activator used to execute '
                 f'commands within a container. '
                 f'Default: {impl._defaults.imgactvtr}',
            default=impl._defaults.imgactvtr,
            choices=cntrimg.ImageActivatorFactory.available(),
            required=False,
            action=impl.ImageActivatorAction,
            imgdir_arg=imgdir_arg
        )

        self.argp.add_argument(
            '-e', '--extras',
            type=str,
            help='A colon-delimited list of paths to additional Python '
                 'packages or modules that bueno will attempt to provide '
                 '(append to sys.path) and make available to the '
                 'specified run script.',
            required=False,
            action=impl.ExtrasAction
        )

        self.argp.add_argument(
            '-p', '--program',
            # Consume the remaining arguments for program's use.
            nargs=argparse.REMAINDER,
            help='Specifies the program to run, optionally '
                 'followed by program-specific arguments.',
            required=True,
            action=impl.ProgramAction
        )

    def _populate_service_config(self) -> None:
        # Remove program from output since it is redundant and because we don't
        # know how it'll be parsed by the given program.
        tmpargs = copy.deepcopy(vars(self.args))
        tmpargs.pop('program')
        self.confd['Configuration'] = tmpargs
        data.add_asset(data.YAMLDictAsset(self.confd, 'run'))

    def _populate_env_config(self) -> None:
        # Host environment.
        self.confd['Host'] = {
            'whoami': host.whoami(),
            'kernel': host.kernel(),
            'kernel_release': host.kernelrel(),
            'hostname': host.hostname(),
            'os_release': host.os_pretty_name()
        }
        # Do this so the YAML output has the 'Host' heading.
        hostd = {'Host': self.confd['Host']}
        data.add_asset(data.YAMLDictAsset(hostd, 'environment'))

    def _populate_config(self) -> None:
        self._populate_service_config()
        self._populate_env_config()

    # TODO(skg) Add more configuration info. pylint: disable=fixme
    def _emit_config(self) -> None:
        # First build up the dictionary containing the configuration used.
        self._populate_config()
        # Then print it out in YAML format.
        utils.yamlp(self.confd, self.prog)

    def _stage_container_image(self) -> None:
        '''
        TODO(skg) Add proper description. Stages container images.
        '''
        imgp = self.args.image
        # The 'we don't need or want to stage paths.'
        if not cntrimg.activator().requires_img_activation():
            return
        if self.args.do_not_stage:
            # We know that imgp cannot be None.
            hlps = 'Unstaged executions require access to ' \
                   'an image directory path.'
            if not os.path.isdir(imgp):
                estr = f'{imgp} is not a directory. Cannot continue.\n{hlps}'
                raise RuntimeError(estr)
            self.inflated_cntrimg_path = imgp
            logger.log(f'# Image path: {imgp}')
            cntrimg.activator().set_img_path(imgp)
            return
        # The 'stage' path.
        logger.emlog('# Staging container image...')
        hlps = 'Staged executions require access to an image tarball path.'
        istf = False
        try:
            istf = tarfile.is_tarfile(imgp)
        except Exception as exception:
            estr = f'{exception}. Cannot continue.\n{hlps}'
            raise RuntimeError(estr) from exception
        # We do this check here so we can raise an exception that isn't caught
        # above because it produces redundant error messages. is_tarfile() can
        # raise exceptions, so that's what the above try/except block is for.
        if not istf:
            raise RuntimeError(
                f'{imgp} is not a tarball. Cannot continue.\n{hlps}'
            )
        self.inflated_cntrimg_path = _ImageStager().stage(imgp)
        # Let the user and image activator know about the image's path.
        logger.log(f'# Staged image path: {self.inflated_cntrimg_path}')
        cntrimg.activator().set_img_path(self.inflated_cntrimg_path)

    def _add_container_data(self) -> None:
        '''
        Adds container data to run data assets.
        '''
        logger.emlog('# Looking for container metadata...')

        # Skip any image activators that do not have build data.
        if not cntrimg.activator().requires_img_activation():
            iact = self.args.image_activator
            logger.log(f'# Note: the {iact} activator has no metadata\n')
            return
        imgdir = self.inflated_cntrimg_path
        # The subdirectory where container data are stored.
        buildl = os.path.join(
            imgdir,
            constants.DATA_DIR,
            constants.SERVICE_LOG_NAME
        )
        # Don't error out if the image doesn't have our data.
        if not os.path.exists(buildl):
            logger.log('# Note: container image provides no data\n')
            return
        logger.log(f'# Adding data from {imgdir}\n')
        mdatadir = 'container'
        data.add_asset(data.FileAsset(buildl, mdatadir))

    def _build_image_activator(self) -> None:
        '''
        Builds the image activator instance.
        '''
        actvtr = self.args.image_activator
        cntrimg.ImageActivatorFactory().build(actvtr)

    def _run(self) -> None:
        pname = os.path.basename(self.args.program[0])
        logger.emlog(f'# Begin Program Output ({pname})')
        _Runner.run(self.args.program)
        logger.emlog('# End Program Output')

    def _write_data(self) -> None:
        outp = experiment.flush_data()
        logger.log(f'# {self.prog} Output Written to {outp}')

    def _experiment_setup(self) -> None:
        experiment.output_path(self.args.output_path)

    def start(self) -> None:
        logger.emlog(f'# Starting {self.prog} at {utils.nows()}')
        logger.log(F"# $ {' '.join(sys.argv)}\n")

        try:
            stime = utils.now()
            self._experiment_setup()
            self._emit_config()
            self._build_image_activator()
            self._stage_container_image()
            self._add_container_data()
            self._run()
            etime = utils.now()

            logger.log(f'# {self.prog} Time {etime - stime}')
            logger.log(f'# {self.prog} Done {utils.nows()}')

            self._write_data()
        except Exception as exception:
            raise exception

# vim: ft=python ts=4 sts=4 sw=4 expandtab
