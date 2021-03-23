#!/bin/bash

#
# Copyright (c)      2021 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

./qa/run-flake8-tests && \
./qa/run-mypy-tests && \
./qa/run-pylint-tests
# ./qa/run-packaging-tests

# vim: ts=4 sts=4 sw=4 expandtab