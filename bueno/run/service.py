#
# Copyright (c) 2019-2020 Triad National Security, LLC
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
from bueno.public import metadata
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
        metadata.add_asset(metadata.FileAsset(argz))
        # Import and run the specified program. argz passed twice for nicer
        # error messages when a user specifies a bogus program.
        spec = importlib.util.spec_from_file_location(argz, argz)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # Save cwd so we can restore it after program execution.
        scwd = os.getcwd()
        try:
            # What's the specified program's cwd?
            pbase = os.path.dirname(argz)
            # cddir to base of given program so relative operations work
            # properly.
            os.chdir(pbase)
            mod.main(argv)
        finally:
            os.chdir(scwd)


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
            raise ValueError(F'{fname} does not end in any of {tfex}.'
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
        stage_cmd = F'{_ImageStager.prun_generate()} ' \
                    F'{cntrimg.activator().tar2dirs(imgp, self.basep)}'
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
                helps = F'{option_string} requires at least one ' \
                        'argument (none provided).\nPlease provide ' \
                        'a path to the program you wish to run, ' \
                        'optionally followed by program-specific arguments.'
                parser.error(helps)
            # Capture and update values[0] to an absolute path.
            prog = values[0] = os.path.abspath(values[0])
            if not os.path.isfile(prog):
                estr = F'{prog} is not a file. Cannot continue.'
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
                estr = F'Cannot access {imgp}'
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
                    estr = F'Cannot access {modpath}'
                    parser.error(estr)
                if not os.path.isdir(modpath):
                    estr = 'Cannot provide regular ' \
                           F'files to {self.dest}: {path}'
                    parser.error(estr)
                sys.path.append(r'{}'.format(modpath))
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
                 'generated files. Default: {}'.format('PWD'),
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
            help=F'Specifies the image activator used to execute '
                 F'commands within a container. '
                 F'Default: {impl._defaults.imgactvtr}',
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
        metadata.add_asset(metadata.YAMLDictAsset(self.confd, 'run'))

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
        metadata.add_asset(metadata.YAMLDictAsset(hostd, 'environment'))

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
                estr = F'{imgp} is not a directory. Cannot continue.\n{hlps}'
                raise RuntimeError(estr)
            self.inflated_cntrimg_path = imgp
            logger.log(F'# Image path: {imgp}')
            cntrimg.activator().set_img_path(imgp)
            return
        # The 'stage' path.
        logger.emlog('# Staging container image...')
        hlps = 'Staged executions require access to an image tarball path.'
        istf = False
        try:
            istf = tarfile.is_tarfile(imgp)
        except Exception as exception:
            estr = F'{exception}. Cannot continue.\n{hlps}'
            raise RuntimeError(estr) from exception
        # We do this check here so we can raise an exception that isn't caught
        # above because it produces redundant error messages. is_tarfile() can
        # raise exceptions, so that's what the above try/except block is for.
        if not istf:
            raise RuntimeError(
                F'{imgp} is not a tarball. Cannot continue.\n{hlps}'
            )
        self.inflated_cntrimg_path = _ImageStager().stage(imgp)
        # Let the user and image activator know about the image's path.
        logger.log(F'# Staged image path: {self.inflated_cntrimg_path}')
        cntrimg.activator().set_img_path(self.inflated_cntrimg_path)

    def _add_container_metadata(self) -> None:
        '''
        Adds container metadata to run metadata assets.
        '''
        logger.emlog('# Looking for container metadata...')

        # Skip any image activators that do not have build metadata.
        if not cntrimg.activator().requires_img_activation():
            iact = self.args.image_activator
            logger.log(F'# Note: the {iact} activator has no metadata\n')
            return
        imgdir = self.inflated_cntrimg_path
        # The subdirectory where container metadata are stored.
        buildl = os.path.join(
            imgdir,
            constants.METADATA_DIR,
            constants.SERVICE_LOG_NAME
        )
        # Don't error out if the image doesn't have our metadata.
        if not os.path.exists(buildl):
            logger.log('# Note: container image provides no metadata\n')
            return
        logger.log(F'# Adding metadata from {imgdir}\n')
        mdatadir = 'container'
        metadata.add_asset(metadata.FileAsset(buildl, mdatadir))

    def _build_image_activator(self) -> None:
        '''
        Builds the image activator instance.
        '''
        actvtr = self.args.image_activator
        cntrimg.ImageActivatorFactory().build(actvtr)

    def _run(self) -> None:
        pname = os.path.basename(self.args.program[0])
        logger.emlog(F'# Begin Program Output ({pname})')
        _Runner.run(self.args.program)
        logger.emlog('# End Program Output')

    @staticmethod
    def getmetasubd(basedir: str) -> str:
        '''
        Returns a unique path rooted at the provided directory.
        '''
        # TODO(skg) The stat load may be huge using this pylint: disable=fixme
        # approach.  Fix at some point. Perhaps have a top-level log that gives
        # us the next available?
        maxt = 1024*2048
        hostn = host.shostname()
        for subd in range(0, maxt):
            path = os.path.join(basedir, utils.dates(), hostn, str(subd))
            if not os.path.isdir(path):
                return path
        errs = F'Cannot find usable metadata directory after {maxt} tries.\n' \
               F'Base output directory searched was: {basedir}'
        raise RuntimeError(errs)

    def _write_metadata(self) -> None:
        base = os.path.join(self.args.output_path, str(experiment.name()))
        outp = impl.getmetasubd(base)
        # Do this here so the output log has the output directory in it.
        logger.log(F'# {self.prog} Output Target: {outp}')
        metadata.write(outp)
        logger.log(F'# {self.prog} Output Written to: {outp}')

    def start(self) -> None:
        logger.emlog(F'# Starting {self.prog} at {utils.nows()}')
        logger.log(F"# $ {' '.join(sys.argv)}\n")

        try:
            stime = utils.now()
            self._emit_config()
            self._build_image_activator()
            self._stage_container_image()
            self._add_container_metadata()
            self._run()
            etime = utils.now()

            logger.log(F'# {self.prog} Time {etime - stime}')
            logger.log(F'# {self.prog} Done {utils.nows()}')

            self._write_metadata()
        except Exception as exception:
            estr = utils.ehorf()
            estr += F'What: {self.prog} error encountered.\n' \
                    F'Why:  {exception}'
            estr += utils.ehorf()
            raise type(exception)(estr) from exception

# vim: ft=python ts=4 sts=4 sw=4 expandtab
