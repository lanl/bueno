#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Container utilities.
'''

from bueno.core import cntrimg
from bueno.public import utils

from typing import (
    Any
)


def run(
    cmd: str,
    echo: bool = True,
    preaction: Any = None,
    postaction: Any = None
) -> None:
    '''
    Runs the given command string from within a container.  Optionally calls
    pre- or post-actions if provided.
    '''
    capture = postaction is not None

    if preaction is not None:
        preargs = {
            'command': cmd
        }
        preaction(**preargs)

    stime = utils.now()
    # TODO(skg) FIXME: I don't like how Activator's __init__ is set up.
    coutput = cntrimg.Activator().impl.run(cmd, echo=echo, capture=capture)
    etime = utils.now()

    if postaction is not None:
        postargs = {
            'command': cmd,
            'exectime': etime - stime,
            'output': coutput
        }
        postaction(**postargs)
