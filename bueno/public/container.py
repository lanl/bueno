#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Container utilities.
'''

from bueno.core import cntrimg


class RunPreAction:
    def __init__(self, cmd):
        self.cmd = cmd


class RunPostAction:
    def __init__(self, cmd, output):
        self.cmd = cmd
        self.output = output


def run(cmd, PreAction=None, PostAction=None):
    '''
    Runs the given command string from within a container.  Optionally
    initializes and calls pre- or post-actions if provided.
    '''
    acers = '{} expects subclass of {{}}'.format(__name__)

    capture = PostAction is not None

    if PreAction is not None:
        if not issubclass(PreAction, RunPreAction):
            raise ValueError(acers.format('RunPreAction'))
        PreAction(cmd)

    coutput = cntrimg.Activator().impl.run(cmd, capture=capture)

    if PostAction is not None:
        if not issubclass(PostAction, RunPostAction):
            raise ValueError(acers.format('RunPostAction'))
        PostAction(cmd, coutput)
