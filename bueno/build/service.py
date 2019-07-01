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
from bueno.core import user

import yaml


class impl(service.Service):
    '''
    Implements the build service.
    '''
    class _defaults:
        '''
        Convenience container for build service defaults.
        '''
        # TODO(skg) Add a proper service description.
        desc = 'The build service builds containers.'

        builder = 'charliecloud'

    def __init__(self, argv):
        self.yaml = None
        super().__init__(impl._defaults.desc, argv)

    def _addargs(self):
        self.argp.add_argument(
            '--builder',
            type=str,
            help='Specifies the container builder to use. '
                 'Default: {}'.format(impl._defaults.builder),
            default=impl._defaults.builder,
            required=False
        )

    def _service_config(self):
        self.confd['Configuration'] = vars(self.args)

    def _env_config(self):
        self.confd['Environment'] = {
            'kernel': opsys.kernel(),
            'kernel version': opsys.kernelrel()
        }

    def _emit_config(self):
        print(yaml.dump(self.confd, default_flow_style=False))

    def _emit_preamble(self):
        print()
        print('# Begin {} Configuration {}'.format(self.prog, utils.now()))

        self._service_config()
        self._env_config()
        self._emit_config()

        print('# End {} Configuration {}'.format(self.prog, utils.now()))
        print()

    def start(self):
        self._emit_preamble()
