#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Utilities for good.
'''

from bueno.public import logger

from datetime import datetime
import yaml


def now():
    '''
    Returns the current date and time.
    '''
    return datetime.now()


def nows():
    '''
    Returns a string representation of the current date and time.
    '''
    return now().strftime('%Y-%m-%d %H:%M:%S')


def chomp(s):
    '''
    Returns a string without trailing newline characters.
    '''
    return s.rstrip()


def syaml(d):
    '''
    Returns YAML string from the provided dictionary.
    '''
    return chomp(yaml.dump(d, default_flow_style=False))


def pyaml(d):
    '''
    Emits YAML output from the provided dictionary.
    '''
    logger.log(syaml(d))


def ehorf():
    '''
    Returns header/footer string used for error messages.
    '''
    return '\n>>!<<\n'


def emptystr(s):
    '''
    Returns True if the provided string is not empty; False otherwise.
    '''
    return not (s and s.strip())
