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


class Singleton(type):
    '''Instances'''
    _insts = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._insts:
            cls._insts[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._insts[cls]
