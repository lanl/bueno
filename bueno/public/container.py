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

import os

from typing import (
    Any,
    Callable,
    List,
    Union
)

from bueno.core import cntrimg
from bueno.core import constants
from bueno.core import metacls

from bueno.public import host
from bueno.public import utils

# Type aliases.
StagingHookCb = Callable[[], str]
ActionCb = Union[Callable[..., None], None]


def _runi(  # pylint: disable=too-many-arguments
        cmds: List[str],
        echo: bool = True,
        check_exit_code: bool = True,
        preaction: ActionCb = None,
        postaction: ActionCb = None,
        user_data: Any = None
) -> None:
    '''
    Private run dispatch.
    '''
    capture_output = postaction is not None

    cmdstr = ' '.join(cmds)

    if preaction is not None:
        preargs = {
            'command': cmdstr,
            'user_data': user_data
        }
        preaction(**preargs)

    stime = utils.now()
    coutput = cntrimg.activator().run(
        cmds,
        echo=echo,
        capture=capture_output,
        check_exit_code=check_exit_code
    )
    etime = utils.now()

    if postaction is not None:
        postargs = {
            'command': cmdstr,
            'start_time': stime,
            'end_time': etime,
            'exectime': (etime - stime).total_seconds(),
            'output': coutput,
            'user_data': user_data
        }
        postaction(**postargs)


def run(  # pylint: disable=too-many-arguments
        cmd: str,
        echo: bool = True,
        check_exit_code: bool = True,
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
        'check_exit_code': check_exit_code,
        'preaction': preaction,
        'postaction': postaction,
        'user_data': user_data
    }
    _runi(**args)


def capture(
        cmd: str,
        check_exit_code: bool = True
) -> str:
    '''
    Executes the provided command and returns a string with the command's
    output.

    See run() for exceptions.
    '''
    runo = cntrimg.activator().run(
        [cmd],
        echo=False,
        verbose=False,
        capture=True,
        check_exit_code=check_exit_code
    )
    return utils.chomp(str().join(runo))


def prun(  # pylint: disable=too-many-arguments
        pexec: str,
        cmd: str,
        echo: bool = True,
        check_exit_code: bool = True,
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
        'check_exit_code': check_exit_code,
        'preaction': preaction,
        'postaction': postaction,
        'user_data': user_data
    }
    _runi(**args)


def build_information() -> List[str]:
    '''
    Returns a list of strings containing captured container and application
    build information. If build information is not available, an empty list is
    returned.
    '''
    buildl = os.path.join(
        cntrimg.activator().get_img_path(),
        constants.METADATA_DIR,
        constants.SERVICE_LOG_NAME
    )
    if not os.path.exists(buildl):
        return []
    return utils.cat(buildl)


def getenv(name: str) -> Union[str, None]:
    '''
    Get an environment variable, return None if it does not exist.
    '''
    res = capture(F'printenv {name}', check_exit_code=False)
    if not utils.emptystr(res):
        return res
    return None


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
