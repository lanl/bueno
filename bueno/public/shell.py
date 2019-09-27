#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Quasi shell-like utilities.
'''

from bueno.public import logger
from bueno.public import utils

import os
import subprocess

# The magic from https://stackoverflow.com/questions/1711970 makes cmd
# quoting a non-issue. Pretty slick... Notice that this is a slightly
# modified version to meet our needs.
bashmagic = 'bash -c \'${0} ${1+$@}\''


def capture(cmd):
    '''
    Executes the provided command and returns a string with the command's
    output.

    See run() for exceptions.
    '''
    res = run(cmd, capture=True, verbose=False)
    return utils.chomp(str().join(res))


def which(cmd):
    '''
    Akin to which(1).

    Returns None if cmd is not found.
    '''
    wcmd = None
    try:
        wcmd = capture('which {}'.format(cmd))
    except ChildProcessError:
        wcmd = None

    return wcmd


def whichl(cmds):
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


def cat(file):
    '''
    Akin to cat(1), but returns a list of strings containing the contents of the
    provided file.

    Raises OSError or IOError on error.
    '''
    lines = list()

    with open(file, 'r') as file:
        for line in file:
            lines.append(line)

    return lines


def cats(file):
    '''
    Akin to cat(1), but returns a string containing the contents of the provided
    file.

    Raises OSError or IOError on error.
    '''
    return str().join(cat(file))


def run(cmd, verbatim=False, echo=False, capture=False, verbose=True):
    '''
    Executes the provided command.

    Returns newline-delimited list of output if capture if True.

    Throws ChildProcessError on error.
    '''
    def getrealcmd(cmd, verbatim):
        if not verbatim:
            return '{} {}'.format(bashmagic, cmd)
        return cmd

    realcmd = getrealcmd(cmd, verbatim)

    if echo:
        logger.log('# $ {}'.format(realcmd))
    # Output list of strings used to (optionally) capture command output.
    olst = list()
    p = subprocess.Popen(
        realcmd,
        shell=True,
        bufsize=1,
        # Enables text mode, making write() et al. happy.
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    # Show progress and store output to a string (if requested).
    while (True):
        stdout = p.stdout.readline()

        if not stdout:
            break
        if capture:
            olst.append(stdout)
        if verbose:
            logger.log(utils.chomp(stdout))

    rc = p.wait()
    if (rc != os.EX_OK):
        e = ChildProcessError()
        e.errno = rc
        es = "Command '{}' returned non-zero exit status.".format(realcmd)
        e.strerror = es
        raise e

    if capture:
        return olst
    else:
        return None
