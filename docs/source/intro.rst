.. Copyright (c) 2019-2021, Triad National Security, LLC
                            All rights reserved.

Introduction
============
System benchmarking provides a means to compare or assess the performance of
hardware or software against a point of reference. Because of the multitude of
factors that ultimately influence a benchmark’s results, reproducibility is
challenging. To aid in this, we developed an extensible software framework named
bueno that provides mechanisms to record and automate many arduous, error-prone
benchmarking tasks: environmental discovery, environmental setup, program
compilation, program execution, data storage, and analysis. Below we summarize
bueno’s software architecture, current feature set, and methodology for
supporting automated, reproducible benchmarking and analysis.

Software Architecture
---------------------
bueno is a small Python-based software framework with minimal external software
dependencies. Its internal software architecture consists of services, which are
accessible through a command-line interface (CLI), and a collection of public
Python modules made available to Python programs executed by bueno’s run
service. The remainder of this section describes both the CLI and public module
services provided by bueno.

Command Line Services
---------------------
CLI services are currently available through ``bueno run``.

The *run* service coordinates container image activation and the execution of
bueno run scripts---a programmatic description of the steps required to conduct a
benchmarking activity. Currently, there are two image activators implemented in
bueno: ``charliecloud`` and ``none``. The former uses Charliecloud to activate a
given container image and the latter is a pass-through to the host.

Module Services
---------------
Because of the diversity among computer platforms, system software, and programs
of interest, the running of programs and subsequent analysis of their generated
outputs is expressed through Python programs executed by bueno’s run service.  A
collection of public Python modules is made available to these programs that aid
in conducting benchmarking activities. Examples include: command dispatch to the
host or container, logging, metadata asset agglomeration, concise expression of
structured experiment generation, and programmable pre- and post-experiment
actions.
