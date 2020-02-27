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

from bueno.core import cntrimg
from bueno.core import constants
from bueno.core import service

from bueno.public import experiment
from bueno.public import host
from bueno.public import logger
from bueno.public import metadata
from bueno.public import utils

from typing import (
    List
)

import argparse
import copy
import importlib.util
import os
import sys
import typing


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
        # Make sure the experiment is setup properly. We can do this only after
        # the module has been loaded.
        experiment._TheExperiment().sanity()
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


class impl(service.Base):
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
                help = '{} requires at least one argument (none provided).\n'\
                       'Please provide a path to the program you wish to run, '\
                       'optionally followed by program-specific arguments.'

                parser.error(help.format(option_string))
            # Capture and update values[0] to an absolute path.
            prog = values[0] = os.path.abspath(values[0])
            if not os.path.isfile(prog):
                es = F'{prog} is not a file. Cannot continue.'
                parser.error(es.format(prog))

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

    def __init__(self, argv: List[str]) -> None:
        super().__init__(impl._defaults.desc, argv)

    def _addargs(self) -> None:
        self.argp.add_argument(
            '-o', '--output-path',
            type=str,
            help='Specifies the base output directory used for all '
                 'generated files. Default: {}'.format('PWD'),
            default=impl._defaults.output_path,
            required=False
        )

        imgdir_arg = self.argp.add_argument(
            '-i', '--image',
            type=str,
            help='Specifies the base container image (directory or tarball).',
            required=True,
            default=impl._defaults.image,
            action=impl.ImageAction
        )

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
            '-p', '--program',
            # Consume the remaining arguments for program's use.
            nargs=argparse.REMAINDER,
            help='Specifies the program to run, optionally '
                 'followed by program-specific arguments.',
            required=True,
            action=impl.ProgramAction
        )

    def _populate_service_config(self) -> None:
        # Remove program from output since it is reduntant and because we don't
        # know how it'll be parsed by the given program.
        tmpargs = copy.deepcopy(vars(self.args))
        tmpargs.pop('program')
        self.confd['Configuration'] = tmpargs
        metadata.add_asset(metadata.YAMLDictAsset(self.confd, 'run'))

    def _populate_sys_config(self) -> None:
        self.confd['Host'] = {
            'whoami': host.whoami(),
            'kernel': host.kernel(),
            'kernel_release': host.kernelrel(),
            'hostname': host.hostname(),
            'os_release': host.os_pretty_name()
        }

    def _populate_config(self) -> None:
        self._populate_service_config()
        self._populate_sys_config()

    # TODO(skg) Add more configuration info.
    def _emit_config(self) -> None:
        # First build up the dictionary containing the configuration used.
        self._populate_config()
        # Add to metadata assets stored to container image.
        metadata.add_asset(metadata.YAMLDictAsset(self.confd, 'environment'))
        # Then print it out in YAML format.
        utils.yamlp(self.confd, self.prog)

    def _add_container_metadata(self) -> None:
        '''
        Adds container metadata to run metadata assets.
        '''
        logger.emlog(F'# Looking for container metadata...')

        # Skip any image activators that do not have build metadata.
        if not cntrimg.Activator().impl.has_metadata():
            ia = self.args.image_activator
            logger.log(F'# Note: the {ia} activator has no metadata\n')
            return

        imgdir = self.args.image
        # The subdirectory where container metadata will be stored.
        mdatadir = 'container'
        logger.log(F'# Adding metadata from {imgdir}\n')
        buildl = os.path.join(
            imgdir,
            constants.METADATA_DIR,
            constants.SERVICE_LOG_NAME
        )
        metadata.add_asset(metadata.FileAsset(buildl, mdatadir))

    def _build_image_activator(self) -> None:
        '''
        Builds the image activator instance.
        '''
        actvtr = self.args.image_activator
        imgdir = self.args.image
        cntrimg.ImageActivatorFactory().build(actvtr, imgdir)

    def _run(self) -> None:
        pname = os.path.basename(self.args.program[0])
        logger.emlog(F'# Begin Program Output ({pname})')
        _Runner.run(self.args.program)
        logger.emlog('# End Program Output')

    def _getmetasubd(self, basedir: str) -> str:
        # TODO(skg) The stat load may be huge using this approach. Fix at some
        # point. Perhaps have a top-level log that gives us the next available?
        maxt = 1024*2048
        for subd in range(0, maxt):
            path = os.path.join(basedir, str(subd))
            if not os.path.isdir(path):
                return path
        errs = F'Cannot find usable metadata directory after {maxt} tries.\n'
        errs += F'Base directory searched was: {basedir}'
        raise RuntimeError(errs)

    def _write_metadata(self) -> None:
        base = os.path.join(self.args.output_path, experiment.name())
        outp = self._getmetasubd(base)
        # Do this here so the output log has the output directory in it.
        logger.log(F'# {self.prog} Output Target: {outp}')
        metadata.write(outp)
        logger.log(F'# {self.prog} Output Written to: {outp}')

    def start(self) -> None:
        logger.emlog(F'# Starting {self.prog} at {utils.nows()}')
        logger.log(F"# $ {' '.join(sys.argv)}\n")

        try:
            stime = utils.now()
            self._build_image_activator()
            self._add_container_metadata()
            self._emit_config()
            self._run()
            etime = utils.now()

            logger.log(F'# {self.prog} Time {etime - stime}')
            logger.log(F'# {self.prog} Done {utils.nows()}')

            self._write_metadata()
        except Exception as e:
            estr = utils.ehorf()
            estr += F'What: {self.prog} error encountered.\n' \
                    F'Why:  {e}'
            estr += utils.ehorf()
            raise type(e)(estr)
