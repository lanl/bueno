#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Stores build metadata and provides metadata asset types.
'''

from bueno.core import utils
from bueno.core import logger
from bueno.core import metacls

from abc import ABC, abstractmethod
from io  import BytesIO

import os
import copy
import shutil


def write(basep):
    '''
    Adds build metadata rooted at basep.
    '''
    _MetaData(basep).write()


class Assets(metaclass=metacls.Singleton):
    '''
    Metadata asset collection.
    '''
    def __init__(self):
        self.assets = []

    def add(self, asset):
        '''
        Adds provided asset to assets.
        '''
        self.assets.append(asset)

    def clear(self):
        '''
        Removes all assets from collection.
        '''
        self.assets = []

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
        # Buffer used to store file contents.
        self.fbuf = BytesIO()
        # Save the contents of the provided file.
        self._buffer()

    def _buffer(self):
        try:
            with open(self.srcf, 'rb') as f:
                shutil.copyfileobj(f, self.fbuf)
        except (OSError, IOError) as e:
            raise(e)

    def _get_fname(self):
        return os.path.basename(self.srcf)

    def deposit(self, basep):
        try:
            opath = os.path.join(basep, self._get_fname())
            self.fbuf.seek(0)
            with open(opath, 'wb+') as f:
                shutil.copyfileobj(self.fbuf, f)
        except (OSError, IOError) as e:
            raise(e)
        finally:
            self.fbuf.seek(os.SEEK_END)


class YAMLAsset(BaseAsset):
    '''
    Convenience YAML (from a dict()) asset.
    '''
    def __init__(self, ydict, fname):
        super().__init__()
        # A deep copy of the provided YAML dictionary.
        self.ydict = copy.deepcopy(ydict)
        # Output file name.
        self.fname = YAMLAsset._name_fixup(fname)

    @staticmethod
    def _name_fixup(name):
        yamlex = '.yaml'
        if not name.endswith(yamlex):
            return name + yamlex
        else:
            return name

    def deposit(self, basep):
        target = os.path.join(basep, self.fname)
        try:
            with open(target, 'w+') as file:
                file.write(utils.syaml(self.ydict))
        except (OSError, IOError) as e:
            raise e

class _LoggerAsset(BaseAsset):
    '''
    bueno logger asset. Notice that this asset is private, unlike the others.
    This asset is private because is added implicitly to the metadata assets.
    '''
    def __init__(self):
        super().__init__()
        self.buildo = 'log.txt'

    def deposit(self, basep):
        logger.log('# Done {}'.format(utils.nows()))
        logger.save(os.path.join(basep, self.buildo))


class _MetaData:
    def __init__(self, basep):
        self.basep = basep
        # The base path where all metadata are stored.
        self.metad = os.path.join(basep, 'bueno')

        self._mkdirs()

    def write(self):
        self._add_default_assets()
        Assets().deposit(self.metad)

    def _mkdirs(self):
        os.makedirs(self.metad, 0o755)

    def _add_default_assets(self):
        Assets().add(_LoggerAsset())
