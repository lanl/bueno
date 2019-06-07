#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

def main():
    import os

    package_name = 'bueno'
    package_vers = '0.1'

    package_setup(package_name, package_vers)

    return os.EX_OK

def package_setup(package_name, package_vers):
    from setuptools import setup

    setup(
        name=package_name,
        version=package_vers,
        description='bueno: Utilities for Automated Benchmarking',
        author='Samuel K. Gutierrez',
        author_email='samuel@lanl.gov',
        license='BSD 3-Clause',
        #NOTE(skg): This can probably be something older. Okay for now.
        python_requires='>=3.6.4',
        packages=[package_name],
        # Package Requirements
        install_requires =[],

        scripts=[
            'bin/bueno'
        ]
    )

if __name__ == '__main__':
    exit(main())
