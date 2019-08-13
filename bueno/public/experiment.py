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

from bueno.public import logger
from bueno.public import shell
from bueno.public import utils

from abc import abstractmethod

import argparse
import copy
import os

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


def readgs(gs, config=None):
    '''
    A convenience routine for reading generate specification files.

    TODO(skg) Add description of formatting rules, etc.

    We accept the following forms:
    # -a/--aarg [ARG_PARAMS] -b/--bargs [ARG PARAMS]
    # -c/--carg [ARG PARAMS] [positional arguments]
    '''
    logger.log('# Reading generate specification file: {}'.format(gs))
    # Emit contents of gs file.
    logger.log(str().join(shell.cat(gs)))

    gsstr = str()
    with open(gs) as f:
        argv = list()
        lines = [x.strip() for x in f.readlines()]
        for l in lines:
            # Interpret as special comment used to specify run-time arguments.
            if l.startswith('# -'):
                # Add to argument list.
                if config is not None:
                    argv.extend(l.lstrip('# ').split())
            # Skip comments.
            elif l.startswith('#'):
                continue
            # Not a comment; append line to generate specification string.
            else:
                gsstr += l
        # Parse arguments if provided an argument parser.
        gsargs = None
        if config is not None:
            if not isinstance(config, CLIConfiguration):
                es = '{} expects an instance of ' \
                     'CLIConfiguration'.format(__name__)
                raise ValueError(es)
            gsargs = parsedargs(config.argparser, argv)
            config.update(gsargs)

    return gsstr


def parsedargs(argprsr, argv):
    # Make a deep copy of the provided argument parser.
    auxap = copy.deepcopy(argprsr)
    aargs = auxap.parse_args(argv)
    # Set defaults to None so we can detect setting of arguments.
    nonedefs = dict()
    for key in vars(aargs):
        nonedefs[key] = None
    auxap.set_defaults(**nonedefs)
    # Parse and return the arguments present in argv.
    return auxap.parse_args(argv)


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


class CLIConfiguration:
    '''
    Command-line interface configuration container and associated utilities.
    '''
    def __init__(self, desc, argv):
        self._desc = desc
        self._argv = argv
        self._prog = os.path.basename(argv[0])

        self._argprsr = argparse.ArgumentParser(
            prog=self._prog,
            description=self._desc,
            allow_abbrev=False
        )
        self.addargs()
        self._args = self.parseargs()

    @property
    def description(self):
        return self._desc

    @property
    def argv(self):
        return self._argv

    @property
    def program(self):
        return self._prog

    @property
    def argparser(self):
        return self._argprsr

    @property
    def args(self):
        return self._args

    @abstractmethod
    def addargs(self):
        pass

    def parseargs(self):
        return self.argparser.parse_args(self.argv[1:])

    def update(self, confns):
        '''
        Update the current configuration using the parsedargs provided through
        confns, a namespace.
        '''
        confd = vars(confns)
        argsd = vars(self._args)
        pcags = vars(parsedargs(self.argparser, self.argv[1:]))

        # Look at the arguments provided in the configuration (gs) file. The
        # order in which the updates occur matter:
        # - confns arguments will overwrite any already set
        # - pcags will overwrite any. This allows the setting of values
        # through a configuration file, while also allowing the ability to
        # overwrite those at run-time through parameters passed to the cli.
        for k, v in argsd.items():
            if confd[k] is not None:
                argsd[k] = confd[k]
            if pcags[k] is not None:
                argsd[k] = pcags[k]
