# # Copyright (c) 2019-2020 Triad National Security, LLC
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
    Iterable,
    List,
    Tuple,
    Optional
)

from bueno.core import mathex
from bueno.core import metacls

from bueno.public import logger
from bueno.public import utils


class _TheExperiment(metaclass=metacls.Singleton):
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
    def name(self, names: str) -> None:
        '''
        Sets the experiment's name.
        '''
        if utils.emptystr(names):
            estr = 'Experiment name cannot be empty.'
            raise RuntimeError(estr)
        self._name = names.strip()


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


def readgs(
        gspath: str,
        config: Optional[CLIConfiguration] = None
) -> Iterable[str]:
    '''
    A convenience routine for reading generate specification files.

    TODO(skg) Add description of formatting rules, semantics, etc. Don't forget
    about yield!

    We accept the following forms:
    # -a/--aarg [ARG_PARAMS] -b/--bargs [ARG PARAMS]
    # -c/--carg [ARG PARAMS] [positional arguments]
    '''
    logger.emlog(F'# Reading Generate Specification File: {gspath}')
    # Emit contents of gs file.
    logger.log('# Begin Generate Specification')
    logger.log(utils.chomp(str().join(utils.cat(gspath))))
    logger.log('# End Generate Specification\n')

    with open(gspath) as file:
        argv = list()
        lines = [x.strip() for x in utils.read_logical_lines(file)]
        for line in lines:
            # Interpret as special comment used to specify run-time arguments.
            if line.startswith('# -'):
                # Add to argument list.
                if config is not None:
                    argv.extend(shlex.split(line.lstrip('# ')))
                continue
            # Skip comments and empty lines.
            if line.startswith('#') or utils.emptystr(line):
                continue
            # Parse arguments if provided an argument parser.
            gsargs = None
            if config is not None:
                if not isinstance(config, CLIConfiguration):
                    estr = F'{__name__} expects an instance of CLIConfiguration'
                    raise ValueError(estr)
                gsargs = parsedargs(config.argparser, argv)
                config.update(gsargs)
            # Not a comment; yield generate specification string.
            yield line
            # Clear out argument list for next round.
            argv = list()


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
    '''
    Container class for custom argparse actions.
    '''
    class RunCmdsAction(argparse.Action):
        '''
        Custom action class used for 'runcmds' argument handling.
        '''
        @typing.no_type_check
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            super().__init__(option_strings, dest, **kwargs)

        @typing.no_type_check
        def __call__(self, parser, namespace, values, option_string=None):
            malf_helps = F'{option_string} malformed input. ' \
                         'An int, int, str, str tuple is excepted.'
            optt = tuple()
            try:
                optt = ast.literal_eval(values)
            except (ValueError, SyntaxError):
                parser.error(malf_helps)
            # Make sure that the evaluated type is tuple.
            if not isinstance(optt, tuple):
                parser.error(malf_helps)
            # Make sure we are dealing with a 4-tuple.
            nopts = len(optt)
            if nopts != 4:
                helps = F'{option_string} requires a 4-tuple of values. ' \
                       F'{nopts} values provided: {optt}.'
                parser.error(helps)
            # Check type of each element.
            if not isinstance(optt[0], int):
                helps = F'{option_string}: The first value must be an int.'
                parser.error(helps)
            if not isinstance(optt[1], int):
                helps = F'{option_string}: The second value must be an int.'
                parser.error(helps)
            if not isinstance(optt[2], str):
                helps = F'{option_string}: The third value must be a string.'
                parser.error(helps)
            if not isinstance(optt[3], str):
                helps = F'{option_string}: The fourth value must be a string.'
                parser.error(helps)
            setattr(namespace, self.dest, optt)


def cli_args_add_runcmds_option(
        clic: CLIConfiguration,
        opt_required: bool = False,
        opt_default: Tuple[int, int, str, str] = (0, 0, '', '')
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


class CannedCLIConfiguration(CLIConfiguration):
    '''
    A 'canned' set of parser arguments common to many (but not all) bueno run
    scripts. This CLI configuration is provided as a convenience for those run
    scripts that can benefit from the options provided.
    '''
    class Defaults:
        '''
        Default values for CannedCLIConfigurations.
        '''
        csv_output = ''
        description = ''
        executable = ''
        input = ''
        name = ''
        runcmds = (0, 0, '', '')

    def __init__(
            self,
            desc: str,
            argv: List[str],
            defaults: CannedCLIConfiguration.Defaults  # noqa: F821
    ) -> None:
        self.defaults = defaults
        super().__init__(desc, argv)

    def addargs(self) -> None:
        self.argparser.add_argument(
            '-o', '--csv-output',
            type=str,
            metavar='CSV_NAME',
            help='Names the generated CSV file produced by a run.',
            required=False,
            default=self.defaults.csv_output
        )

        self.argparser.add_argument(
            '-d', '--description',
            type=str,
            metavar='DESC',
            help='Describes the experiment.',
            required=False,
            default=self.defaults.description
        )

        self.argparser.add_argument(
            '-e', '--executable',
            type=str,
            metavar='EXEC',
            help="Specifies the executable's path.",
            required=False,
            default=self.defaults.executable
        )

        self.argparser.add_argument(
            '-i', '--input',
            type=str,
            metavar='INP',
            help='Specifies the path to an experiment input file.',
            required=False,
            default=self.defaults.input
        )

        self.argparser.add_argument(
            '-n', '--name',
            type=str,
            help='Names the experiment.',
            required=False,
            default=self.defaults.name
        )
        # Add pre-canned options to deal with experiment.runcmds() input.
        cli_args_add_runcmds_option(
            self,
            opt_required=False,
            opt_default=self.defaults.runcmds
        )


def _runcmds_nargs(line: str, res: str) -> int:
    '''
    Private function that returns the number of arguments found in line given a
    regular expression.
    '''
    nargs = 0
    for _ in re.finditer(res, line, flags=re.X):
        nargs += 1
    return nargs


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
    if _runcmds_nargs(nfun, vidx_res) == 0:
        # We didn't find at least one variable.
        estr = F'{__name__}.{fname} syntax error: ' \
               'At least one variable must be present. ' \
               F"'nidx' was not found in the following expression:\n{nfun}"
        raise SyntaxError(estr)
    # Generate the requisite values.
    nvals = list()
    nidx = start
    regex = re.compile(vidx_res, flags=re.X)
    while True:
        nval = mathex.evaluate(regex.sub(str(nidx), nfun))
        if nval > stop:
            break
        nvals.append(nval)
        nidx += 1
    # Now generate the run commands.
    # Regex string used to find %n variables in spec expressions.
    n_res = '%n'
    if _runcmds_nargs(spec, n_res) == 0:
        wstr = F"# WARNING: '{n_res}' not found in " \
               F'the following expression:\n# {spec}'
        logger.emlog(wstr)
    regex = re.compile(n_res)
    cmds = list()
    for idx in nvals:
        cmds.append(regex.sub(str(idx), spec))
    return cmds

# vim: ft=python ts=4 sts=4 sw=4 expandtab
