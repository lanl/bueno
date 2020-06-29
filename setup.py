#!/usr/bin/env python3

#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#
# type: ignore

'''
The setup script for the bueno project.
'''

import os
import re
import sys

from setuptools import setup, find_packages


def get_minimum_python_vers():
    '''
    Returns the minimum Python version required for this package. Raises a
    RuntimeError if the version cannot be determined.
    '''
    verline = open('./bueno/_minpyversion.txt').read()
    resr = re.search(
        r"^__bueno_minimum_python_version_str__ = ['\']([^'\']*)['\']",
        verline
    )
    if resr:
        return resr.group(1)
    raise RuntimeError('Cannot determine minimum Python version.')


def package_setup(package_name, package_vers):
    '''
    Package setup routine.
    '''
    setup(
        name=package_name,
        version=package_vers,
        description='bueno: Utilities for Automated Benchmarking',
        author='Samuel K. Gutierrez',
        author_email='samuel@lanl.gov',
        license='BSD 3-Clause',
        python_requires='>={}'.format(get_minimum_python_vers()),
        include_package_data=True,
        packages=find_packages(),
        # Package Requirements
        install_requires=[
            'pyyaml'
        ],
        scripts=[
            'bin/bueno'
        ]
    )


def main():
    '''
    The main entry point for this program.
    '''
    package_name = 'bueno'
    # IMPORTANT: Never change manually, always use bumpversion.
    package_vers = '0.0.1'

    package_setup(package_name, package_vers)

    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())

# vim: ft=python ts=4 sts=4 sw=4 expandtab
