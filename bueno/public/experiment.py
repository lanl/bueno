#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Public experiment utilities for good.
'''

import argparse
import ast
import copy
import os
import re
import shlex
import typing

from abc import abstractmethod

from typing import (
    Any,
    Dict,
    List,
    Optional
)

from bueno.core import mathex
from bueno.core import metacls

from bueno.public import logger
from bueno.public import utils


class _TheExperiment(metaclass=metacls.Singleton):  # pylint: disable=R0903
    '''
    The experiment singleton that encapsulates experiment information.
    '''
    def __init__(self) -> None:
        self._name = 'unnamed-experiment'

    @property
    def name(self) -> str:
        '''
        Returns the experiment's name.
        '''
        return self._name

    @name.setter
    def name(self, name: str) -> None:  # pylint: disable=W0621
        '''
        Sets the experiment's name.
        '''
        if utils.emptystr(name):
            estr = 'Experiment name cannot be empty.'
            raise RuntimeError(estr)
        self._name = name.strip()


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
        '''
        Returns the desription used to initialize the encapsulated
        ArgumentParser.
        '''
        return self._desc

    @property
    def argv(self) -> List[str]:
        '''
        Returns the argument list used during instance initialization.
        '''
        return self._argv

    @property
    def program(self) -> str:
        '''
        Returns the basename of argv[0], i.e., the program name.
        '''
        return self._prog

    @property
    def argparser(self) -> argparse.ArgumentParser:
        '''
        Returns the internal ArgumentParser instance.
        '''
        return self._argprsr

    @property
    def args(self) -> argparse.Namespace:
        '''
        Returns the ArgumentParser Namespace acquired after argument parsing.
        '''
        return self._args

    @abstractmethod
    def addargs(self) -> None:
        '''
        Abstract method that shall be used by derived classes to add a custom
        collection of arguments via self.argparser.add_argument(), for example.
        CLIConfiguration will call this function at the appropriate time.
        '''

    def parseargs(self) -> argparse.Namespace:
        '''
        Thin abstraction around argparser.parse_args().
        '''
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
        for key, _ in argsd.items():
            if confd[key] is not None:
                argsd[key] = confd[key]
            if pcags[key] is not None:
                argsd[key] = pcags[key]


def name(ename: Optional[str] = None) -> Optional[str]:
    '''
    Experiment name getter/setter. If a name string is provided, then it acts as
    a setter, acting as a getter otherwise.
    '''
    if ename is None:
        return _TheExperiment().name
    if not isinstance(ename, str):
        estr = F'{__name__}.name() expects a string.'
        raise ValueError(estr)
    _TheExperiment().name = ename
    return None


def generate(spec: str, *args: Any) -> List[str]:
    '''
    Given a string containing string.format() replacement fields and a variable
    number of iterables, attempt to generate an iterable collection of strings
    generated from the provided specification and corresponding inputs.
    '''
    if not isinstance(spec, str):
        estr = F'{__name__}.generate() expects a string specification.'
        raise ValueError(estr)

    argg = zip(* args)

    return [spec.format(*a) for a in argg]


def readgs(gspath: str, config: Optional[CLIConfiguration] = None) -> str:
    '''
    A convenience routine for reading generate specification files.

    TODO(skg) Add description of formatting rules, etc.

    We accept the following forms:
    # -a/--aarg [ARG_PARAMS] -b/--bargs [ARG PARAMS]
    # -c/--carg [ARG PARAMS] [positional arguments]
    '''
    logger.emlog(F'# Reading Generate Specification File: {gspath}')
    # Emit contents of gs file.
    logger.log('# Begin Generate Specification')
    logger.log(utils.chomp(str().join(utils.cat(gspath))))
    logger.log('# End Generate Specification\n')

    gsstr = str()
    with open(gspath) as file:
        argv = list()
        lines = [x.strip() for x in file.readlines()]
        for line in lines:
            # Interpret as special comment used to specify run-time arguments.
            if line.startswith('# -'):
                # Add to argument list.
                if config is not None:
                    argv.extend(shlex.split(line.lstrip('# ')))
            # Skip comments.
            elif line.startswith('#'):
                continue
            # Not a comment; append line to generate specification string.
            else:
                gsstr += line
        # Parse arguments if provided an argument parser.
        gsargs = None
        if config is not None:
            if not isinstance(config, CLIConfiguration):
                estr = F'{__name__} expects an instance of CLIConfiguration'
                raise ValueError(estr)
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


class CLIArgsAddActions:
    class RunCmdsAction(argparse.Action):
        '''
        Custom action class used for 'runcmds' argument handling.
        '''
        @typing.no_type_check
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            super().__init__(option_strings, dest, **kwargs)

        @typing.no_type_check
        def __call__(self, parser, namespace, values, option_string=None):
            optt = ()
            try:
                optt = ast.literal_eval(values)
            except ValueError:
                help = F'{option_string} malformed input. ' \
                        'An int, int, str, str tuple is excepted.'
                parser.error(help)
            nopts = len(optt)
            if nopts != 4:
                help = F'{option_string} requires a 4-tuple of values. ' \
                       F'{nopts} values provided: {optt}.'
                parser.error(help)
            if not isinstance(optt[0], int):
                help = F'{option_string}: The first value must be an int.'
                parser.error(help)
            if not isinstance(optt[1], int):
                help = F'{option_string}: The second value must be an int.'
                parser.error(help)
            if not isinstance(optt[2], str):
                help = F'{option_string}: The third value must be a string.'
                parser.error(help)
            if not isinstance(optt[3], str):
                help = F'{option_string}: The fourth value must be a string.'
                parser.error(help)
            setattr(namespace, self.dest, optt)


def cli_args_add_runcmds_options(
        clic: CLIConfiguration,
        opt_required: bool = False,
        opt_default: str = ''
) -> argparse.Action:
    '''
    Adds parser options to the given CLIConfiguration instance for handling
    runcmds input. Adds --runcmds and a custom action to parse its input.
    '''
    return clic.argparser.add_argument(
        '--runcmds',
        type=str,
        metavar='4TUP',
        help="Specifies the input 4-tuple used to generate run commands. "
             "For example, \"0, 16, 'srun -n %%n', 'nidx + 1'\"",
        required=opt_required,
        default=opt_default,
        action=CLIArgsAddActions.RunCmdsAction
    )


def runcmds(
        start: int,
        stop: int,
        spec: str,
        nfun: str
) -> List[str]:
    '''
    TODO(skg) Add proper description.
    - start: The start index of nidx.
    - stop: The termination value for nfun(nidx) for some value nidx.
    - spec: The run specification template having the following variables:
    -   %n: The number of processes to run.
    '''
    # XXX(skg) I wish we could use something like pylint: disable=W0511
    # __name__ for this...
    fname = 'runcmds'
    # Regex string used to find variables in nfun expressions.
    vidx_res = '''\
    (         # Start of capture group 1
    \\b       # Start of whole word search
    nidx      # Variable literal
    \\b       # End of whole word search
    )         # End of capture group 1
    '''

    def _nargs(line: str, res: str) -> int:
        nargs = 0
        for m in re.finditer(res, line, flags=re.X):
            nargs += 1
        return nargs

    def _nfun_nvar(s: str, res: str) -> int:
        nvars = 0
        for m in re.finditer(res, s, flags=re.X):
            nvars += 1
        return nvars

    # Make sure that the provided start and stop values make sense.
    if start < 0 or stop < 0:
        estr = F'{__name__}.{fname} start and ' \
               'stop must both be positive values.'
        raise ValueError(estr)
    if start > stop:
        estr = F'{__name__}.{fname} value error: ' \
               'start cannot be less than stop.'
        raise ValueError(estr)
    # Find all variables in the provided function specification string. Also
    # enforce that *at least one* variable is provided.
    nvars = _nfun_nvar(nfun, vidx_res)
    # We didn't find at least one variable.
    if nvars == 0:
        estr = F'{__name__}.{fname} syntax error: ' \
               'At least one variable must be present. ' \
               F'nidx was not found in the following expression:\n{nfun}'
        raise SyntaxError(estr)
    # Generate the requisite values.
    ns = list()
    nidx = start
    regex = re.compile(vidx_res, flags=re.X)
    while True:
        n = mathex.evaluate(regex.sub(str(nidx), nfun))
        if n > stop:
            break
        ns.append(n)
        nidx += 1
    # Now generate the run commands.
    # Regex string used to find %n variables in spec expressions.
    n_res = '%n'
    nargs = _nargs(spec, n_res)
    if nargs == 0:
        ws = F'# WARNING: {n_res} not found in ' \
             F'the following expression:\n# {spec}'
        logger.emlog(ws)
    regex = re.compile(n_res)
    cmds = list()
    for idx in ns:
        cmds.append(regex.sub(str(idx), spec))
    return cmds

# vim: ft=python ts=4 sts=4 sw=4 expandtab
