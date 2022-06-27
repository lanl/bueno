# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Bueno(PythonPackage):
    """Bueno: Well-Provenanced Benchmarking"""

    homepage    = "https://lanl.github.io/bueno"
    url         = "https://github.com/lanl/bueno/archive/refs/tags/v0.0.1.tar.gz"
    git         = "https://github.com/lanl/bueno.git"

    maintainers = ['rbberger']

    version("master", branch="master")

    depends_on("py-pyyaml")
    depends_on("py-lark@1.0.0")
    depends_on("py-pika@1.2.0")

    depends_on('py-setuptools', type='build')
