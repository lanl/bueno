#
# Copyright (c) 2019-2020 Triad National Security, LLC
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
from bueno.public import utils

from abc import abstractmethod

from typing import (
    Any,
    Dict,
    List,
    Optional
)

import argparse
import copy
import os
import shlex


class _TheExperiment(metaclass=metacls.Singleton):
    '''
    The experiment singleton that encapsulates experiment information.
    '''
    def __init__(self) -> None:
        self._name = 'unnamed-experiment'

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if utils.emptystr(name):
            es = 'Experiment name cannot be empty.'
            raise RuntimeError(es)
        self._name = name.strip()

    def sanity(self) -> None:
        pass


class CLIConfiguration:
    '''
    Command-line interface configuration container and associated utilities.
    '''
    def __init__(self, desc: str, argv: List[str]) -> None:
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
    def description(self) -> str:
        return self._desc

    @property
    def argv(self) -> List[str]:
        return self._argv

    @property
    def program(self) -> str:
        return self._prog

    @property
    def argparser(self) -> argparse.ArgumentParser:
        return self._argprsr

    @property
    def args(self) -> argparse.Namespace:
        return self._args

    @abstractmethod
    def addargs(self) -> None:
        pass

    def parseargs(self) -> argparse.Namespace:
        return self.argparser.parse_args(self.argv[1:])

    def update(self, confns: argparse.Namespace) -> None:
        '''
        Update the current configuration using the parsedargs provided through
        confns, a namespace.
        '''
        confd = vars(confns)
        argsd = vars(self.args)
        pcags = vars(parsedargs(self.argparser, self.argv[1:]))
        # Look at the arguments provided in the configuration (gs) file. The
        # order in which the updates occur matters:
        # - confns arguments will overwrite any already set
        # - pcags will overwrite any. This allows the setting of values
        # through a configuration file, while also allowing the ability to
        # overwrite those at run-time through parameters passed to the cli.
        for k, v in argsd.items():
            if confd[k] is not None:
                argsd[k] = confd[k]
            if pcags[k] is not None:
                argsd[k] = pcags[k]


def name(n: Optional[str] = None) -> Optional[str]:
    '''
    Experiment name getter/setter. If a name string is provided, then it acts as
    a setter, acting as a getter otherwise.
    '''
    if n is None:
        return _TheExperiment().name
    elif not isinstance(n, str):
        es = F'{__name__}.name() expects a string.'
        raise RuntimeError(es)
    else:
        _TheExperiment().name = n
        return None


def generate(spec: str, *args: Any) -> List[str]:
    '''
    Given a string containing string.format() replacement fields and a variable
    number of iterables, attempt to generate an iterable collection of strings
    generated from the provided specification and corresponding inputs.
    '''
    if not isinstance(spec, str):
        es = F'{__name__}.generate() expects a string specification.'
        raise ValueError(es)

    argg = zip(* args)

    return [spec.format(*a) for a in argg]


def readgs(gs: str, config: Optional[CLIConfiguration] = None) -> str:
    '''
    A convenience routine for reading generate specification files.

    TODO(skg) Add description of formatting rules, etc.

    We accept the following forms:
    # -a/--aarg [ARG_PARAMS] -b/--bargs [ARG PARAMS]
    # -c/--carg [ARG PARAMS] [positional arguments]
    '''
    logger.emlog(F'# Reading Generate Specification File: {gs}')
    # Emit contents of gs file.
    logger.log('# Begin Generate Specification')
    logger.log(utils.chomp(str().join(utils.cat(gs))))
    logger.log('# End Generate Specification\n')

    gsstr = str()
    with open(gs) as f:
        argv = list()
        lines = [x.strip() for x in f.readlines()]
        for l in lines:
            # Interpret as special comment used to specify run-time arguments.
            if l.startswith('# -'):
                # Add to argument list.
                if config is not None:
                    argv.extend(shlex.split(l.lstrip('# ')))
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
                es = F'{__name__} expects an instance of CLIConfiguration'
                raise ValueError(es)
            gsargs = parsedargs(config.argparser, argv)
            config.update(gsargs)

    return gsstr


def parsedargs(
    argprsr: argparse.ArgumentParser,
    argv: List[str]
) -> argparse.Namespace:
    '''
    TODO(skg) add a proper description.
    '''
    # Make a deep copy of the provided argument parser.
    auxap = copy.deepcopy(argprsr)
    aargs = auxap.parse_args(argv)
    # Set defaults to None so we can detect setting of arguments.
    nonedefs: Dict[Any, None] = dict()
    for key in vars(aargs):
        nonedefs[key] = None
    auxap.set_defaults(**nonedefs)
    # Parse and return the arguments present in argv.
    return auxap.parse_args(argv)

# vim: ft=python ts=4 sts=4 sw=4 expandtab
