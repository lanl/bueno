#
# Copyright (c) 2019-2021 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Core metadata types.
'''

import copy
import io
import os
import shutil

from abc import ABC, abstractmethod
from pathlib import Path
from types import ModuleType

from typing import (
    Any,
    Dict,
    List,
    Union
)

from bueno.core import constants
from bueno.core import metacls

from bueno.public import logger
from bueno.public import utils


class BaseAsset(ABC):
    '''
    Abstract base metadata asset class.
    '''
    @abstractmethod
    def write(self, basep: str) -> None:
        '''
        Abstract method used to write the contents of a derived class to a
        location rooted at the specified base path.
        '''


class FileAsset(BaseAsset):
    '''
    File asset.
    '''
    def __init__(self, srcf: str, subd: Union[str, None] = None):
        super().__init__()
        # Absolute path to source file asset.
        self.srcf = os.path.abspath(srcf)
        # Optional subdirectory to store the provided file.
        self.subd = subd

    def _get_fname(self) -> str:
        return os.path.basename(self.srcf)

    def write(self, basep: str) -> None:
        realbasep = basep
        if self.subd:
            realbasep = os.path.join(basep, self.subd)
            os.makedirs(realbasep, 0o755, exist_ok=True)
        opath = os.path.join(realbasep, self._get_fname())
        shutil.copy2(self.srcf, opath)


class PythonModuleAsset(FileAsset):
    '''
    Special file asset used for extra imported modules.
    '''
    def __init__(self, mod: ModuleType) -> None:
        if not isinstance(mod, ModuleType):
            estr = F'{self.__class__} expects a module.'
            raise ValueError(estr)
        # Absolute path to source file asset.
        fpath = Path(os.path.abspath(mod.__file__))
        # Module's parent directory to store the provided module file.
        pdir = fpath.parent.parts[-1]
        super().__init__(str(fpath), str(pdir))


class StringIOAsset(BaseAsset):
    '''
    StringIO asset.
    '''
    def __init__(
            self,
            srcios: io.StringIO,
            fname: str,
            subd: Union[str, None] = None
    ):
        super().__init__()
        # XXX(skg): Are there any file-descriptor-like pylint: disable=W0511
        # structures that cannot be safely copied here? The print() in write()
        # should make a copy of the data, so maybe that's enough?
        # The StringIO instance of which we are storing its contents.
        self.srcios = copy.deepcopy(srcios)
        # The name used to store the contents of the provided StringIO instance.
        self.fname = fname
        # Optional subdirectory to store the specified data.
        self.subd = subd

    def write(self, basep: str) -> None:
        realbasep = basep
        if self.subd:
            realbasep = os.path.join(basep, self.subd)
            os.makedirs(realbasep, 0o755, exist_ok=True)
        opath = os.path.join(realbasep, self.fname)
        with open(opath, mode='w', encoding='utf8') as file:
            print(self.srcios.getvalue(), file=file, end='')


class YAMLDictAsset(BaseAsset):
    '''
    Convenience YAML (from a dict()) asset.
    '''
    def __init__(self, ydict: Dict[Any, Any], fname: str) -> None:
        super().__init__()
        # A deep copy of the provided YAML dictionary.
        self.ydict = copy.deepcopy(ydict)
        # Output file name.
        self.fname = fname

    @property
    def fname(self) -> str:
        '''
        Returns the output file name.
        '''
        return self._fname

    @fname.setter
    def fname(self, name: str) -> None:
        '''
        Sets the output file name.
        '''
        yamlex = '.yaml'
        if not name.endswith(yamlex):
            self._fname = name + yamlex
        else:
            self._fname = name

    def write(self, basep: str) -> None:
        '''
        Writes the contents of the YAMLDictAsset to a file rooted at the
        specified path.
        '''
        target = os.path.join(basep, self._fname)
        with open(target, 'w+', encoding='utf8') as file:
            file.write(utils.yamls(self.ydict))


class LoggerAsset(BaseAsset):
    '''
    bueno logger asset.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.buildo = constants.SERVICE_LOG_NAME

    def write(self, basep: str) -> None:
        logger.write(os.path.join(basep, self.buildo))


class _MetaData:
    def __init__(self, basep: str) -> None:
        # The base path where metadata are stored.
        self._basep = basep
        os.makedirs(self.basep, 0o755, exist_ok=True)

    def write(self) -> None:
        '''
        Writes out all the metadata assets.
        '''
        _MetaData._add_default_assets()
        _Assets().write(self.basep)

    @staticmethod
    def _add_default_assets() -> None:
        '''
        Adds default metadata assets to _Assets collection.
        '''
        _Assets().add(LoggerAsset())

    @property
    def basep(self) -> str:
        '''
        Returns the base path where metadata are stored.
        '''
        return self._basep

    @basep.setter
    def basep(self, basep: str) -> None:
        '''
        Sets the base path where metadata are stored.
        '''
        self._basep = basep


class _Assets(metaclass=metacls.Singleton):
    '''
    Metadata asset collection.
    '''
    def __init__(self) -> None:
        self.assets: List[BaseAsset] = []

    def add(self, asset: BaseAsset) -> None:
        '''
        Adds provided asset to assets.
        '''
        self.assets.append(asset)

    def clear(self) -> None:
        '''
        Removes all assets from collection.
        '''
        self.assets = []

    def write(self, basep: str) -> None:
        '''
        Writes metadata contained in assets.
        '''
        logger.log(F'# Writing Metadata Assets at {utils.nows()}')
        for asset in self.assets:
            asset.write(basep)


def write(basep: str) -> None:
    '''
    Writes build metadata rooted at basep.
    '''
    _MetaData(basep).write()


def add_asset(asset: BaseAsset) -> None:
    '''
    Adds a metadata asset to the collection of assets to be written.
    '''
    _Assets().add(asset)

# vim: ft=python ts=4 sts=4 sw=4 expandtab
