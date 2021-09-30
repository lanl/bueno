#!/bin/bash

#
# Copyright (c)      2021 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

# Straightforward tests for the bueno command.

set -e

function test_start()
{
    me=$(basename "$0")
    echo
    echo "$me .................................................."
    set -x
}

function test_end()
{
    set +x
    me=$(basename "$0")
    echo "$me ..............................................done"
}

# vim: ts=4 sts=4 sw=4 expandtab
