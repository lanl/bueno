#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
'''

import subprocess
import sys


# TODO(skg): Add logging redirect, tee, etc through *args.
def run(cmd):
    p = subprocess.Popen(
            cmd,
            shell=True,
            # Enables text mode, making write() et al. happy.
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    # Show progress.
    while (True):
        stdout = p.stdout.readline()
        sys.stdout.write(stdout)
        sys.stdout.flush()

        if not stdout and p.poll() is not None:
            break

    rc = p.wait()
    if (rc != 0):
        e = ChildProcessError()
        e.errno = rc
        es = "Command '{}' returned non-zero exit status {}.".format(cmd, rc)
        e.strerror = es
        raise e
