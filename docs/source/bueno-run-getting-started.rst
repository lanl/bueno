Run Scripts: Getting Started
############################

``bueno run`` coordinates container image activation and the execution of bueno
run scripts---a programmatic description of the steps required to conduct a
benchmarking activity. Currently, there are two image activators implemented in
bueno: ``charliecloud`` and ``none``. The former uses `Charliecloud
<https://hpc.github.io/charliecloud/>`_ to activate a given container image and
the latter is a pass-through to the host.

Hello World!
------------
Below is the source code of the simplest bueno run script named ``hello.py``.
Please note that the source code contains helpful comments that aid in
understanding fundamental bueno run script structure.

.. literalinclude:: ../../examples/hello/hello.py

In the following example, we execute ``hello.py`` using the ``none`` (i.e.,
*host pass-through*) image activator.  To execute the script, run the following
command (assumes ``hello.py`` is stored in your current working directory):

.. code-block:: console

   $ bueno run -a none -p hello.py

This program invocation should produce console output similar to the following:

.. literalinclude:: ./includes/hello-output.txt

More bueno run Help
-------------------
Additional run service information is provided by the output of ``bueno run
--help``.
