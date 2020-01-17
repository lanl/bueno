.. Copyright (c) 2019-2020, Triad National Security, LLC
                            All rights reserved.

bueno Development
=================


Building RPMs
#############

Prerequisites
- rpm-build

.. code-block:: console

   $ python3 setup.py bdist_rpm


MyPy
####

.. code-block:: console

   $ python3 -m mypy --strict .
