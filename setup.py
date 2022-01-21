#
# Copyright (c) 2019-2021 Triad National Security, LLC
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
import sys

from setuptools import setup, find_packages

__min_py_version__ = (3, 7)

# Before we perform the package setup, we need to check the minimum Python
# version manually because some versions of pip don't respect python_requires.
if sys.version_info < __min_py_version__:
    sys.exit('!!! bueno Requires Python >= {} !!!'.format(__min_py_version__))


def _get_3rd_party_path(name, version):
    path = os.path.join(os.getcwd(), '3rd-party', name)
    return F'file://localhost/{path}/{version}.tar.gz'


def package_setup(package_name, package_vers):
    '''
    Package setup routine.
    '''
    setup(
        name=package_name,
        version=package_vers,
        description='bueno: Well-Provenanced Benchmarking',
        author='Samuel K. Gutierrez',
        author_email='samuel@lanl.gov',
        license='BSD 3-Clause',
        package_data={package_name: ['py.typed']},
        include_package_data=True,
        packages=find_packages(),
        # Package Requirements
        install_requires=[
            'pyyaml',
            F'pika @ {_get_3rd_party_path("pika", "1.2.0")}',
            F'lark @ {_get_3rd_party_path("lark", "1.0.0")}'
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
