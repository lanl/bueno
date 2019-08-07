#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Experiment utilities for good.
'''

from bueno.core import metacls

from bueno.public import utils

import copy

# TODO(skg) Add a convenience function that allows for the specification of a
# list (in priority order) of executables. The first one found wins!


def name(n=None):
    '''
    Experiment name getter/setter. If a name string is provided, then it acts as
    a setter, acting as a getter otherwise.
    '''
    if n is None:
        return _TheExperiment().name
    elif not isinstance(n, str):
        es = '{}.name() expects a string.'.format(__name__)
        raise RuntimeError(es)
    else:
        _TheExperiment().name = n


def generate(spec, *args):
    '''
    Given a string containing string.format() replacement fields and a variable
    number of iterables, attempt to generate an iterable collection of strings
    generated from the provided specification and corresponding inputs.
    '''
    if not isinstance(spec, str):
        es = '{}.generate() expects a string specification.'.format(__name__)
        raise ValueError(es)
    argg = zip(* args)
    return [spec.format(*a) for a in argg]


def readgs(gs, argp=None):
    '''
    A convenience routine for reading generate specification files.

    TODO(skg) Add description of formatting rules, etc.

    We accept the following forms:
    # -a/--aarg [ARG_PARAMS] -b/--bargs [ARG PARAMS]
    # -c/--carg [ARG PARAMS] [positional arguments]
    '''
    gsstr = str()
    with open(gs) as f:
        argv = list()
        lines = [x.strip() for x in f.readlines()]
        for l in lines:
            # Interpret as special comment used to specify run-time arguments.
            if l.startswith('# -'):
                # Add to argument list.
                if argp is not None:
                    argv.extend(l.lstrip('# ').split())
            # Skip comments.
            elif l.startswith('#'):
                continue
            # Not a comment; append line to generate specification string.
            else:
                gsstr += l
        # Parse arguments if provided an argument parser.
        gsargs = None
        if argp is not None:
            gsargs = parsedargs(argp, argv)
    return gsstr, gsargs

def parsedargs(argp, argv):
    # Make a deep copy of the provided argument parser.
    auxap = copy.deepcopy(argp)
    # Known args, remaining (not used) = auxap.parse_known_args(argv)
    kargs, _ = auxap.parse_known_args(argv)
    # Set defaults to None so we can detect setting of arguments.
    nonedefs = dict()
    for key in vars(kargs):
        nonedefs[key] = None
    auxap.set_defaults(**nonedefs)
    # Parse the arguments present in file.
    pargs, _ = auxap.parse_known_args(argv)

    return pargs


class _TheExperiment(metaclass=metacls.Singleton):
    '''
    The experiment singleton TODO(skg) add a nice description.
    '''
    def __init__(self):
        self._name = str()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if utils.emptystr(name):
            es = 'Experiment name cannot be empty.'
            raise RuntimeError(es)
        self._name = name.strip()

    def sanity(self):
        fixs = 'Please set it via experiment.{0}(VALUE).\n' \
               'For example:\n' \
               'from bueno.public import experiment\n' \
               'experiment.{0}(\'aname\')\n'
        if utils.emptystr(self.name):
            es = 'Experiment name is not set. '
            es += fixs.format('name')
            raise RuntimeError(es)
