#!/bin/bash

#
# Copyright (c) 2020-2021 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

usage() {
cat << EOF

Usage:
    build-docs.sh [OPTION]
Options:
    -h|--help      Show this message and exit
    -n|--no-backup Do not create a documentation backup
EOF
}

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

backup_html() {
    echo "Backing up html to html-backup"
    rm -rf html-backup
    [ -d html ] && cp -r html html-backup
}

main() {
    local do_backup="yes"

    for i in "$@"; do
        case "$1" in
            -h|--help)
                usage
                exit 0;
                ;;
            -n|--no-backup)
                do_backup="no"
                shift
                ;;
            *)
                echo
                echo "Unrecognized option: $i"
                echo
                usage
                exit 1;
                ;;
        esac
    done

    verify_prereqs
    if [[ "$do_backup" == "yes" ]]; then
        backup_html
    fi
    cddocs
    echo "Building Documentation in $PWD";
    git rm -rf --ignore-unmatch html
    make html
    mv build/html .
    git add html
    echo "All done!"
}

set -e
main "${@:1}"

# vim: ts=4 sts=4 sw=4 expandtab
