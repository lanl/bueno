#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Core metadata types.
'''

from bueno.core import utils
from bueno.core import logger
from bueno.core import metacls

from abc import ABC, abstractmethod

import os
import copy
import shutil


class Assets(metaclass=metacls.Singleton):
    '''
    Metadata asset collection.
    '''
    def __init__(self):
        self.assets = list()

    def add(self, asset):
        '''
        Adds provided asset to assets.
        '''
        self.assets.append(asset)

    def clear(self):
        '''
        Removes all assets from collection.
        '''
        self.assets = list()

    def deposit(self, basep):
        '''
        Deposits metadata contained in current assets.
        '''
        for a in self.assets:
            a.deposit(basep)


class BaseAsset(ABC):
    '''
    Abstract base metadata asset class.
    '''
    def __init__(self):
        super().__init__()

    @abstractmethod
    def deposit(self, basep):
        pass


class FileAsset(BaseAsset):
    '''
    File asset.
    '''
    def __init__(self, srcf, subd=None):
        super().__init__()
        # Path to source file asset.
        self.srcf = srcf
        # Optional subdirectory to store the provided file.
        self.subd = subd

    def _get_fname(self):
        return os.path.basename(self.srcf)

    def deposit(self, basep):
        realbasep = basep
        if self.subd:
            realbasep = os.path.join(basep, self.subd)
            os.makedirs(realbasep, 0o755)
        opath = os.path.join(realbasep, self._get_fname())
        shutil.copy2(self.srcf, opath)


class YAMLDictAsset(BaseAsset):
    '''
    Convenience YAML (from a dict()) asset.
    '''
    def __init__(self, ydict, fname):
        super().__init__()
        # A deep copy of the provided YAML dictionary.
        self.ydict = copy.deepcopy(ydict)
        # Output file name.
        self.fname = YAMLDictAsset._name_fixup(fname)

    @staticmethod
    def _name_fixup(name):
        yamlex = '.yaml'
        if not name.endswith(yamlex):
            return name + yamlex
        else:
            return name

    def deposit(self, basep):
        target = os.path.join(basep, self.fname)
        with open(target, 'w+') as file:
            file.write(utils.syaml(self.ydict))


class LoggerAsset(BaseAsset):
    '''
    bueno logger asset.
    '''
    def __init__(self):
        super().__init__()
        self.buildo = 'log.txt'

    def deposit(self, basep):
        logger.log('# Done {}'.format(utils.nows()))
        logger.save(os.path.join(basep, self.buildo))
