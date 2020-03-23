#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Convenience metaclasses.
'''

from typing import (
    Any,
    Dict
)


class Singleton(type):
    '''
    Metaclass for singletons.
    '''
    # Instance storage.
    _insts: Dict[Any, Any] = dict()

    def __call__(cls: Any, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._insts:
            cls._insts[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._insts[cls]

# vim: ft=python ts=4 sts=4 sw=4 expandtab
