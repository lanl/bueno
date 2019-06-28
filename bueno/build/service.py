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

    def _emit_service_config(self):
        print('# Configuration')
        for k, v in vars(self.args).items():
            print(' - {}: {}'.format(k, v))

    def _emit_env_config(self):
        print('# Environment Configuration')
        print(' - Kernel: {}'.format(opsys.kernel()))
        print(' - Kernel Release: {}'.format(opsys.kernelrel()))

    def _emit_preamble(self):
        print()
        print('# Starting : {}'.format(utils.now()))

        self._emit_service_config()
        self._emit_env_config()

        print('# Finish: {}'.format(utils.now()))
        print()

    def start(self):
        self._emit_preamble()
