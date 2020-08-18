#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Host utilities.
'''

from typing import (
    List,
    Union
)

import os
import shutil
import subprocess

from bueno.core import constants

from bueno.public import logger
from bueno.public import utils


def kernel() -> str:
    '''
    Returns the kernel name.
    '''
    return capture('uname -s')


def kernelrel() -> str:
    '''
    Returns the kernel release.
    '''
    return capture('uname -r')


def hostname() -> str:
    '''
    Returns the host computer's name.
    '''
    return capture('hostname')


def shostname() -> str:
    '''
    Returns the host computer's short name.
    '''
    return capture('hostname -s')


def whoami() -> str:
    '''
    Akin to whoami(1).
    '''
    return capture('whoami')


def os_pretty_name() -> str:
    '''
    Returns the host's pretty name as reported by /etc/os-release.
    '''
    name = 'Unknown'
    try:
        with open('/etc/os-release') as osrel:
            for line in osrel:
                if not line.startswith('PRETTY_NAME='):
                    continue
                name = utils.chomp(line.split('=')[1]).strip('"')
                break
    except (OSError, IOError):
        pass

    return name


def capture(cmd: str) -> str:
    '''
    Executes the provided command and returns a string with the command's
    output.

    See run() for exceptions.
    '''
    res = run(cmd, capture_output=True, verbose=False)
    return utils.chomp(str().join(res))


def which(cmd: str) -> Union[str, None]:
    '''
    Akin to which(1).

    Returns None if cmd is not found.
    '''
    return shutil.which(cmd)


def whichl(cmds: List[str]) -> Union[str, None]:
    '''
    Akin to which(1), but accepts a list of commands to search for. The first
    command found by which() is returned.

    Returns None if none of the provided commands are found.
    '''
    for cmd in cmds:
        wcmd = which(cmd)
        if wcmd is not None:
            return wcmd

    return None


def tmpdir() -> str:
    '''
    Returns tmpdir.
    '''
    tdir = os.getenv('TMPDIR')
    if tdir is not None:
        return tdir
    return '/tmp'


def run(
        cmd: str,
        verbatim: bool = False,
        echo: bool = False,
        capture_output: bool = False,
        verbose: bool = True
) -> List[str]:
    '''
    Executes the provided command.

    Returns newline-delimited list of output if capture_output if True.

    Throws ChildProcessError on error.
    '''
    def getrealcmd(cmd: str, verbatim: bool) -> str:
        if not verbatim:
            return F'{constants.BASH_MAGIC} {cmd}'
        return cmd

    realcmd = getrealcmd(cmd, verbatim)

    if echo:
        logcmd = realcmd
        # No need to let the user know that we are using magic here.
        if not verbatim:
            # +1 to account for the space added after magic.
            logcmd = realcmd[len(constants.BASH_MAGIC) + 1:]
        logger.log(F'# $ {logcmd}')

    # Output list of strings used to (optionally) capture command output.
    olst: List[str] = list()
    spo = subprocess.Popen(
        realcmd,
        shell=True,
        bufsize=1,
        # Enables text mode, making write() et al. happy.
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    # Show progress and store output to a string (if requested).
    while True:
        stdout = spo.stdout.readline()

        if not stdout:
            break
        if capture_output:
            olst.append(stdout)
        if verbose:
            logger.log(utils.chomp(stdout))

    wrc = spo.wait()
    if wrc != os.EX_OK:
        cpe = ChildProcessError()
        cpe.errno = wrc
        estr = F"Command '{realcmd}' returned non-zero exit status."
        cpe.strerror = estr
        raise cpe

    return olst

# vim: ft=python ts=4 sts=4 sw=4 expandtab
