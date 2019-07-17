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

from bueno.core import utils
from bueno.core import logger

import subprocess
import os


def capture(cmd, chomp=True):
    '''
    Executes the provided command and returns a string with the commands output.

    See run() for exceptions.
    '''
    res = run(cmd, capture=True)
    if chomp:
        res = utils.chomp(res)

    return res


def which(cmd):
    wcmd = None
    try:
        wcmd = capture('which {}'.format(cmd))
    except ChildProcessError:
        wcmd = None
    return wcmd


def run(cmd, echo=True, capture=False):
    '''
    Executes the provided command.

    Throws ChildProcessError on error.
    '''
    if echo:
        logger.log('# $ {}'.format(cmd))
    # Output string used to (optionally) capture command output.
    ostr = str()
    p = subprocess.Popen(
            cmd,
            shell=True,
            # Enables text mode, making write() et al. happy.
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    # Show progress and store output to a string (if requested).
    while (True):
        stdout = p.stdout.readline()
        if capture:
            ostr += stdout
        else:
            logger.log(utils.chomp(stdout))

        if not stdout and p.poll() is not None:
            break

    rc = p.wait()
    if (rc != os.EX_OK):
        e = ChildProcessError()
        e.errno = rc
        es = "Command '{}' returned non-zero exit status.".format(cmd)
        e.strerror = es
        raise e

    if capture:
        return ostr
