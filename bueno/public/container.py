#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Public container activation interfaces.
'''

from bueno.core import cntrimg
from bueno.core import metacls

from bueno.public import host
from bueno.public import utils

from typing import (
    Any,
    Callable,
    List,
    Union
)

import os

# Type alias.
StagingHookCb = Callable[[], str]
ActionCb = Union[Callable[..., None], None]


def _runi(
    cmds: List[str],
    echo: bool = True,
    preaction: ActionCb = None,
    postaction: ActionCb = None,
    user_data: Any = None
) -> None:
    '''
    Private run dispatch.
    '''
    capture = postaction is not None

    cmdstr = ' '.join(cmds)

    if preaction is not None:
        preargs = {
            'command': cmdstr,
            'user_data': user_data
        }
        preaction(**preargs)

    stime = utils.now()
    # TODO(skg) FIXME: I don't like how Activator's __init__ is set up.
    coutput = cntrimg.Activator().impl.run(cmds, echo=echo, capture=capture)
    etime = utils.now()

    if postaction is not None:
        postargs = {
            'command': cmdstr,
            'exectime': etime - stime,
            'output': coutput,
            'user_data': user_data
        }
        postaction(**postargs)


def run(
    cmd: str,
    echo: bool = True,
    preaction: Any = None,
    postaction: Any = None,
    user_data: Any = None
) -> None:
    '''
    Runs the given command string from within a container.  Optionally calls
    pre- or post-actions if provided.
    '''
    args = {
        'cmds': [cmd],
        'echo': echo,
        'preaction': preaction,
        'postaction': postaction,
        'user_data': user_data
    }
    _runi(**args)


def prun(
    pexec: str,
    cmd: str,
    echo: bool = True,
    preaction: Any = None,
    postaction: Any = None,
    user_data: Any = None
) -> None:
    '''
    Executes the given parallel run command string from within a container.
    Optionally calls pre- or post-actions if provided.

    The primary reason we have a separate command for running serial and
    parallel workloads is because we need to position image activator commands
    between the string containing the pexec string (e.g., mpiexec -n 3 -N 1 -mca
    foo bar) and the cmd string (e.g., nbody --decomp 221). Parsing these
    strings in a general, reliable way is challenging. This way is much easier.
    '''
    args = {
        'cmds': [pexec, cmd],
        'echo': echo,
        'preaction': preaction,
        'postaction': postaction,
        'user_data': user_data
    }
    _runi(**args)


class ImageStager(metaclass=metacls.Singleton):
    '''
    Public container image stager singleton meant to provide some
    programmability to the container image staging process.
    '''
    def __init__(self) -> None:
        self._staging_cmd_hook: StagingHookCb
        self.install_default_staging_cmd_hook()

    @property
    def staging_cmd_hook(self) -> StagingHookCb:
        '''
        Returns the staging command hook if one is installed. Returns None
        otherwise.
        '''
        return self._staging_cmd_hook

    @staging_cmd_hook.setter
    def staging_cmd_hook(self, callback_fn: StagingHookCb) -> None:
        '''
        Sets the staging command hook to a user-provided callback function.
        '''
        self._staging_cmd_hook = callback_fn

    def install_default_staging_cmd_hook(self) -> None:
        '''
        Installs the default staging command hook.
        '''
        self.staging_cmd_hook = ImageStager._srun_staging_cmd_hook

    @staticmethod
    def _srun_staging_cmd_hook() -> str:
        cmd = 'srun'
        if host.which(cmd) is None:
            helps = 'A custom image stager can be set via ' \
                    'ImageStager.staging_cmd_hook.'
            raise RuntimeError(F'{cmd} not found.\n{helps}')
        envvars = ['SLURM_JOB_NUM_NODES', 'SLURM_NNODES']
        varvals = list(
            filter(lambda x: x is not None, [os.getenv(x) for x in envvars])
        )
        if not varvals:
            errs = 'Cannot determine the number of nodes in your job.'
            raise RuntimeError(errs)
        nnodes = varvals[0]
        return F'{cmd} -n {nnodes} -N {nnodes}'

# vim: ft=python ts=4 sts=4 sw=4 expandtab
