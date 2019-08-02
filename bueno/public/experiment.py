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

# TODO(skg) Add a convenience function that allows for the specification of a
# list (in priority order) of executables. The first one found wins!


def name(n=None):
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
        # TODO(skg) Add proper error message that calls out this function.
        raise ValueError('src must be a string')
    argg = zip(* args)
    # For efficiency use generator.
    return (spec.format(*a) for a in argg)


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
               'experiment.{0}(VALUE)\n'
        if utils.emptystr(self.name):
            es = 'Experiment name is not set. '
            es += fixs.format('name')
            raise RuntimeError(es)
