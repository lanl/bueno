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
from bueno.core import utils
from bueno.core import opsys
from bueno.core import io

from bueno.build import builder

import os


class impl(service.Base):
    '''
    Implements the build service.
    '''
    class _defaults:
        '''
        Convenience container for build service defaults.
        '''
        # TODO(skg) Add a proper service description.
        desc = 'The build service builds containers.'
        # The name of the builder back-end.
        builder = 'charliecloud'
        # Path to the build specification (e.g., a Dockerfile specification).
        spec_path = os.getcwd()
        # Path to save any generated files.
        output_path = os.getcwd()

    def __init__(self, argv):
        super().__init__(impl._defaults.desc, argv)

        self.builder = None

    def _addargs(self):
        self.argp.add_argument(
            '--builder',
            type=str,
            help='Specifies the container builder back-end to use. '
                 'Default: {}'.format(impl._defaults.builder),
            default=impl._defaults.builder,
            choices=builder.Factory.available(),
            required=False
        )

        self.argp.add_argument(
            '--spec',
            type=str,
            help='Base path to build specification file (e.g., a Dockerfile). '
                 'Default: {}'.format(impl._defaults.spec_path),
            default=impl._defaults.spec_path,
            required=False
        )

        self.argp.add_argument(
            '--tag',
            type=str,
            help='Specifies the container name (required).',
            required=True
        )

        self.argp.add_argument(
            '--output-path',
            type=str,
            help='Specifies the output directory used for all generated files. '
                 'Default: {}'.format(impl._defaults.output_path),
            default=impl._defaults.output_path,
            required=False
        )

    def _populate_service_config(self):
        self.confd['Configuration'] = vars(self.args)

    def _populate_env_config(self):
        self.confd['Environment'] = {
            'kernel': opsys.kernel(),
            'kernel release': opsys.kernelrel(),
            'hostname': opsys.hostname(),
            'os release': opsys.pretty_name()
        }

    # TODO(skg) Add more configuration info.
    def _emit_config(self):
        print('# Begin {} Configuration (YAML)'.format(self.prog))
        # First build up the dictionary containing the configuration used.
        self._populate_service_config()
        self._populate_env_config()
        # Then print it out in YAML format.
        utils.pyaml(self.confd)
        print('# End {} Configuration (YAML)'.format(self.prog))

    def _do_build(self):
        self.builder = builder.Factory.build(**vars(self.args))
        self.builder.start()

    def start(self):
        stime = utils.now()

        try:
            self._emit_config()
            self._do_build()
        except Exception as e:
            io.ehorf()
            io.eprint('What: {} error encountered.\n'
                      'Why:  {}'.format(self.prog, e))
            io.ehorf()
            raise e

        etime = utils.now()
        print('# {} Time {}'.format(self.prog, etime - stime))
