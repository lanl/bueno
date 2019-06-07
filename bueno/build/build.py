#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

class Builder :
    def __init__(self):
        self.test = 42

    def hi(self):
        print(self.test)
