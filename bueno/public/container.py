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

from bueno.public import utils


class RunPreAction:
    '''
    Base RunPreAction class.
    '''
    def __init__(self, **kwargs):
        self.data = kwargs


class RunPostAction:
    '''
    Base RunPostAction class.
    '''
    def __init__(self, **kwargs):
        self.data = kwargs


def run(cmd, PreAction=None, PostAction=None):
    '''
    Runs the given command string from within a container.  Optionally
    initializes and calls pre- or post-actions if provided.
    '''
    acers = '{} expects {{}} subclass.'.format(__name__)

    capture = PostAction is not None

    if PreAction is not None:
        preargs = {
            'command': cmd
        }
        if not issubclass(PreAction, RunPreAction):
            raise ValueError(acers.format('RunPreAction'))
        PreAction(**preargs)

    stime = utils.now()
    coutput = cntrimg.Activator().impl.run(cmd, capture=capture)
    etime = utils.now()

    if PostAction is not None:
        postargs = {
            'command': cmd,
            'exectime': etime - stime,
            'output': coutput
        }
        if not issubclass(PostAction, RunPostAction):
            raise ValueError(acers.format('RunPostAction'))
        PostAction(**postargs)
