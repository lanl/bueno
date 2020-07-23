#!/bin/bash

#
# Copyright (c)      2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

cddocs() {
    tdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    pushd "$tdir" || exit 1
}

verify_prereqs() {
    local prereqs=(git sphinx-build)

    for prereq in "${prereqs[@]}"; do
        if [[ ! $(command -v "$prereq") ]]; then
            echo
            echo "*** $prereq not found. Cannot continue ***" && exit 1
            echo
        fi
    done
}

main() {
    set -e

    verify_prereqs
    cddocs

    echo "Building Documentation in $PWD"
    git rm -rf html
    make html
    mv build/html .
    git add html
    echo "All done!"
}

main

# vim: ts=4 sts=4 sw=4 expandtab
