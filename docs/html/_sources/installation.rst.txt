.. Copyright (c) 2019-2021, Triad National Security, LLC
                            All rights reserved.

Installing bueno
================

User Installation With pip
--------------------------
In a terminal perform the following (assumes a bash-like shell).

.. code-block:: console

   $ git clone git@github.com:lanl/bueno.git
   $ cd bueno # The directory in which setup.py is located.
   $ python3 -m pip install --user .

Add bueno's installation prefix to your ``PATH``.

.. code-block:: console

   $ export PY_USER_BIN=$(python3 -c 'import site; print(site.USER_BASE + "/bin")')
   $ export PATH=$PY_USER_BIN:$PATH

Now, the ``bueno`` command should be available for use.

User Uninstallation with pip
----------------------------
.. code-block:: console

   $ python3 -m pip uninstall bueno

Optional Software Dependencies
------------------------------

Charliecloud: User-Defined Software Stacks for HPC
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Container technology is used to improve the likelihood of experimental
reproducibility in bueno. Currently, bueno supports unprivileged container
activation through `Charliecloud <https://github.com/hpc/charliecloud>`_. To
enable this capability in bueno, Charliecloud must be installed. Once you have
obtained a recent release of Charliecloud from `here
<https://github.com/hpc/charliecloud/releases>`_, execute the following
commands.

.. code-block:: console

   $ ./configure
   $ make
   $ cd bin
   $ PATH=$PWD:$PATH
