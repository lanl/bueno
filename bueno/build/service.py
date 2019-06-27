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


class impl(service.Service):
    '''
    Implements the build service.
    '''
    class _defaults:
        '''
        Convenience container for build service defaults.
        '''
        builder = 'charliecloud'

    def __init__(self, argv):
        # TODO(skg) Add a proper service description.
        self.desc = 'The build service builds containers.'

        super().__init__(self.desc, argv)

    def _addargs(self):
        self.argp.add_argument(
            '--builder',
            type=str,
            help='Specifies the container builder to use. '
                 'Default: {}'.format(impl._defaults.builder),
            default=impl._defaults.builder,
            required=False
        )

    def _emit_preamble(self):
        pass

    def start(self):
        self._emit_preamble()
