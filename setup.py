#!/usr/bin/env python3

#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

import re


def get_version():
    verline = open('./bueno/_version.py').read()
    sr = re.search(r"^__version__ = ['\']([^'\']*)['\']", verline)
    if sr:
        return sr.group(1)
    else:
        raise RuntimeError('Cannot determine version from version file.')

def main():
    import os

    package_name = 'bueno'
    package_vers = get_version()

    package_setup(package_name, package_vers)

    return os.EX_OK


def package_setup(package_name, package_vers):
    '''
    Package setup routine.
    '''
    from setuptools import setup, find_packages

    setup(
        name=package_name,
        version=package_vers,
        description='bueno: Utilities for Automated Benchmarking',
        author='Samuel K. Gutierrez',
        author_email='samuel@lanl.gov',
        license='BSD 3-Clause',
        python_requires='>=3.3',
        packages=find_packages(),
        # Package Requirements
        install_requires=[
            'pyyaml'
        ],

        scripts=[
            'bin/bueno'
        ]
    )


if __name__ == '__main__':
    exit(main())
