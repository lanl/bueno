.. Copyright (c) 2019-2022, Triad National Security, LLC
                            All rights reserved.

bueno Development
=================
This section is meant for bueno developers. Here we document how to accomplish
activities common to bueno development, testing, and documentation.

Automated Testing
-----------------
Before pushing code, run bueno's automated test suite locally and make certain
all tests pass.

.. code-block:: console

   $ ./qa/run-qa-suite.sh

Releasing
---------
Install bumpversion

.. code-block:: console

   $ python3 -m pip install --user bumpversion

Understand bueno's versioning convention:

.. code-block:: console

   major.minor.patch[-{rc}]

Use bumpversion to roll a new release.

.. code-block:: console

   # Test creating a release candidate.
   $ bumpversion --dry-run --verbose rc
   # If everything looks good, actually create the release candidate.
   $ bumpversion --verbose rc
   # Push new tag
   $ git push --tags

Building the Documentation
--------------------------
Install Sphinx and the RTD theme.

.. code-block:: console

   $ python3 -m pip install --user sphinx
   $ python3 -m pip install --user sphinx_rtd_theme

Build the documentation.

.. code-block:: console

   $ cd docs
   $ ./build-docs.sh

If the project's code structure has changed in a meaningful way (e.g., the
addition of a package or module), it may be necessary to re-run the following
before executing ``make html``.

.. code-block:: console

   $ cd docs
   $ sphinx-apidoc -f -o source/ ../bueno

Building RPMs
-------------
Prerequisites: ``rpm-build``

.. code-block:: console

   $ python3 setup.py bdist_rpm

bueno Source Documentation
--------------------------
.. toctree::
   :maxdepth: 4

   bueno
