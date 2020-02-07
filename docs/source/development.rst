.. Copyright (c) 2019-2020, Triad National Security, LLC
                            All rights reserved.

bueno Development
=================

Building RPMs
-------------
Prerequisites: ``rpm-build``

.. code-block:: console

   $ python3 setup.py bdist_rpm

MyPy
----
.. code-block:: console

   $ python3 -m mypy --strict .

Building the Documentation
--------------------------
Install Sphinx and the RTD theme.

.. code-block:: console

   $ python3 -m pip install --user sphinx
   $ python3 -m pip install --user sphinx_rtd_theme

Build the documentation.

.. code-block:: console

   $ cd docs
   $ make html

If the project's code structure has changed in a meaningful way (e.g., the
addition of a package or module), it may be necessary to re-run the following
before executing ``make html``.

.. code-block:: console

   $ cd docs
   $ sphinx-apidoc -f -o source/ ../bueno

bueno Source Documentation
--------------------------
.. toctree::
   :maxdepth: 4

   bueno
