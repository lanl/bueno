#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
The run service module.
'''

from bueno.core import utils
from bueno.core import opsys
from bueno.core import logger
from bueno.core import service
from bueno.core import metadata

import os
import argparse
import importlib.util


class _Runner:
    @staticmethod
    def run(argv):
        '''
        Loads and executes the run program specified at argv[0], passing along
        all program-specific arguments to the program (argv).
        '''
        if len(argv) == 0:
            raise RuntimeError('Invalid argv format provided.')
        prog = argv[0]
        if not os.path.isfile(prog):
            es = '{} is not a file. Cannot continue.'.format(prog)
            raise RuntimeError(es)
        # Import and run the specified program.
        spec = importlib.util.spec_from_file_location(prog, prog)
        prog = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prog)
        prog.main(argv)


class impl(service.Base):
    '''
    Implements the run service.
    '''
    class _defaults:
        '''
        Convenience container for run service defaults.
        '''
        # TODO(skg) Add a proper description.
        desc = 'The run service runs programs.'
        # Path to save any generated files.
        output_path = os.getcwd()

    def __init__(self, argv):
        super().__init__(impl._defaults.desc, argv)

    def _addargs(self):
        self.argp.add_argument(
            '-p', '--program',
            # Consume the remaining arguments for program's use.
            nargs=argparse.REMAINDER,
            help='Specifies the program to run with optional '
                 'program-specific arguments that follow.',
            required=True
        )

        self.argp.add_argument(
            '-o', '--output-path',
            type=str,
            help='Specifies the base output directory used for all '
                  'generated files. Default: {}'.format('PWD'),
            default=impl._defaults.output_path,
            required=False
        )

    def _populate_service_config(self):
        self.confd['Configuration'] = vars(self.args)
        metadata.Assets().add(metadata.YAMLDictAsset(self.confd, 'run'))

    def _populate_env_config(self):
        self.confd['Environment'] = {
            'whoami': opsys.whoami(),
            'kernel': opsys.kernel(),
            'kernel_release': opsys.kernelrel(),
            'hostname': opsys.hostname(),
            'os_release': opsys.pretty_name()
        }

    # TODO(skg) Add more configuration info.
    def _emit_config(self):
        logger.log('# Begin {} Configuration (YAML)'.format(self.prog))
        # First build up the dictionary containing the configuration used.
        self._populate_service_config()
        self._populate_env_config()
        # Then print it out in YAML format.
        utils.pyaml(self.confd)
        # Add to metadata assets stored to container image.
        metadata.Assets().add(metadata.YAMLDictAsset(self.confd, 'environment'))
        logger.log('# End {} Configuration (YAML)'.format(self.prog))

    def _run(self):
        logger.log('\n# Begin program output')
        _Runner.run(self.args.program)
        logger.log('# End program output\n')

    def _write_metadata(self):
        base = self.args.output_path
        subd = 'TODO'
        outp = os.path.join(base, subd)
        metadata.write(base, subd)
        logger.log('# Run Output Written to: {}'.format(outp))

    def start(self):
        logger.log('# Starting {} at {}'.format(self.prog, utils.nows()))
        stime = utils.now()

        try:
            self._emit_config()
            self._run()
        except Exception as e:
            estr = utils.ehorf()
            estr += 'What: {} error encountered.\n' \
                    'Why:  {}'.format(self.prog, e)
            estr += utils.ehorf()
            raise type(e)(estr)

        etime = utils.now()
        logger.log('# {} Time {}'.format(self.prog, etime - stime))
        logger.log('# {} Done {}'.format(self.prog, utils.nows()))

        self._write_metadata()
