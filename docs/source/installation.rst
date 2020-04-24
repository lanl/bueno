.. Copyright (c) 2019-2020, Triad National Security, LLC
                            All rights reserved.

Installing bueno
================

User Installation With pip
--------------------------
In a terminal perform the following (assumes a bash-like shell).

.. code-block:: console

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
