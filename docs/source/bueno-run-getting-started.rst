bueno Run Scripts: Getting Started
##################################

``bueno run`` coordinates container image activation and the execution of
bueno run scripts---a programmatic description of the steps required to conduct a
benchmarking activity. Currently, there are two image activators implemented in
bueno: ``charliecloud`` and ``none``. The former uses Charliecloud to activate a
given container image and the latter is a pass-through to the host.

Hello World!
------------
Below is the source code of the simplest bueno run script.

.. literalinclude:: ../../examples/hello/hello.py

To execute the script, run the following command:

.. code-block:: console

   $ bueno run -a none -p hello.py
