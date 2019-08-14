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

from bueno.core import metacls

from bueno.public import utils
from bueno.public import logger

from abc import ABC, abstractmethod

import os
import copy
import shutil


def write(basep):
    '''
    Writes build metadata rooted at basep.
    '''
    _MetaData(basep).write()

def add_asset(asset):
    '''
    Adds a metadata asset to the collection of assets to be written.
    '''
    _Assets().add(asset)


class _MetaData:
    def __init__(self, basep):
        # The base path where all metadata are stored.
        self.basep = basep
        os.makedirs(self.basep, 0o755)

    def write(self):
        self._add_default_assets()
        _Assets().write(self.basep)

    def _add_default_assets(self):
        _Assets().add(LoggerAsset())

    def set_basep(basep):
        self.basep = basep

    def get_basep():
        return sefl.basep


class _Assets(metaclass=metacls.Singleton):
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

    def write(self, basep):
        '''
        Writes metadata contained in assets.
        '''
        for a in self.assets:
            a.write(basep)


class BaseAsset(ABC):
    '''
    Abstract base metadata asset class.
    '''
    def __init__(self):
        super().__init__()

    @abstractmethod
    def write(self, basep):
        pass


class FileAsset(BaseAsset):
    '''
    File asset.
    '''
    def __init__(self, srcf, subd=None):
        super().__init__()
        # Absolute to source file asset.
        self.srcf = os.path.abspath(srcf)
        # Optional subdirectory to store the provided file.
        self.subd = subd

    def _get_fname(self):
        return os.path.basename(self.srcf)

    def write(self, basep):
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
        self.fname = fname

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, name):
        yamlex = '.yaml'
        if not name.endswith(yamlex):
            self._fname = name + yamlex
        else:
            self._fname = name

    def write(self, basep):
        target = os.path.join(basep, self._fname)
        with open(target, 'w+') as file:
            file.write(utils.syaml(self.ydict))


class LoggerAsset(BaseAsset):
    '''
    bueno logger asset.
    '''
    def __init__(self):
        super().__init__()
        self.buildo = 'log.txt'

    def write(self, basep):
        # logger.log('# Done {}'.format(utils.nows()))
        logger.write(os.path.join(basep, self.buildo))
