#
# Copyright (c) 2019-2020 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Core container image infrastructure.
'''

from bueno.core import constants
from bueno.core import metacls

from bueno.public import host

from abc import ABC, abstractmethod
from typing import (
    List,
    Optional
)

import os


class BaseImageActivator(ABC):
    '''
    Abstract base class for container image activators.
    '''
    def __init__(self) -> None:
        super().__init__()
        # Optional image path.
        self._imgp: str = ''

    def get_img_path(self) -> str:
        '''
        Returns the image path used for container image activation.
        '''
        return self._imgp

    @abstractmethod
    def set_img_path(self, img_path: str) -> None:
        '''
        Sets the image path used for container image activation. RuntimeError is
        raised if an invalid path is provided.
        '''
        pass

    @abstractmethod
    def run(
        self,
        cmds: List[str],
        echo: bool = True,
        capture: bool = False,
        verbose: bool = True
    ) -> List[str]:
        '''
        Runs the specified command in a container. By default the executed
        command is emitted echoed before its execution.
        '''
        pass

    @abstractmethod
    def requires_img_activation(self) -> bool:
        '''
        Returns whether or not the image activator instance requires image
        activation.
        '''
        pass

    @abstractmethod
    def tar2dirs(self, src: str, dst: str) -> str:
        '''
        Returns a command string capable of extracting the contents of the
        provided source tarball to the provided base destination.
        '''
        pass


class Activator(metaclass=metacls.Singleton):
    '''
    Image activator singleton.
    '''
    def __init__(self, imgactvtr: Optional[BaseImageActivator] = None) -> None:
        # XXX(skg): I know this is silly, but this form makes the type checker
        # happy. Perhaps we should rethink and refactor this and surrounding
        # code.
        if imgactvtr is not None:
            self.imgactvtr = imgactvtr

    @property
    def impl(self) -> BaseImageActivator:
        return self.imgactvtr


class ImageActivatorFactory:
    '''
    The container image activator factory.
    '''
    # Modify this list as image activators change.
    items = [
        ('charliecloud', lambda x: CharlieCloudImageActivator()),
        ('none', lambda x: NoneImageActivator())
    ]

    @staticmethod
    def available() -> List[str]:
        '''
        Returns list of available container names.
        '''
        return [i[0] for i in ImageActivatorFactory.items]

    @staticmethod
    def known(sname: str) -> bool:
        '''
        Returns a boolean indicating whether or not the provided container name
        is known (i.e., recognized) by bueno.
        '''
        return sname in ImageActivatorFactory.available()

    @staticmethod
    def build(activator_name: str) -> None:
        try:
            aidx = ImageActivatorFactory.available().index(activator_name)
        except Exception:
            ers = 'Unknown container image activator requested: {}'
            raise RuntimeError(ers.format(activator_name))
        # Initialize the activator singleton with the proper implementation.
        Activator(ImageActivatorFactory.items[aidx][1](''))  # type: ignore


class CharlieCloudImageActivator(BaseImageActivator):
    '''
    The CharlieCloud image activator.
    '''
    def __init__(self) -> None:
        super().__init__()

        self.runcmd = 'ch-run'

        if not host.which(self.runcmd):
            inyp = 'Is it in your PATH?'
            notf = "'{}' not found. " + inyp
            errs = notf.format(self.runcmd)
            raise RuntimeError(errs)

    def run(
        self,
        cmds: List[str],
        echo: bool = True,
        capture: bool = False,
        verbose: bool = True
    ) -> List[str]:
        # Charliecloud activation command string.
        cc = F'{self.runcmd} {self.get_img_path()}'
        bm = F'{constants.BASH_MAGIC}'
        # First command.
        cmdf = cmds[0]
        # The rest of the commands.
        cmdr = ' '.join(cmds[1:])
        # Are multiple command strings provided?
        multicmd = len(cmds) > 1
        # Default command string if a single command is provided.
        cmdstr = F'{cc} -- {bm} {cmdf}'
        if multicmd:
            cmdstr = F'{cmdf} {cc} --join -- {bm} {cmdr}'
        runargs = {
            'verbatim': True,
            'echo': echo,
            'capture': capture,
            'verbose': verbose
        }
        return host.run(cmdstr, **runargs)

    def set_img_path(self, img_path: str) -> None:
        if not os.path.isdir(img_path):
            hlp = 'Directory expected.'
            ers = F'Invalid container image path detected: {img_path}\n{hlp}'
            raise RuntimeError(ers)
        self._imgp = img_path

    def requires_img_activation(self) -> bool:
        return True

    def tar2dirs(self, src: str, dst: str) -> str:
        return F'ch-tar2dir {src} {dst}'


class NoneImageActivator(BaseImageActivator):
    '''
    The non-image-activator activator. Just a passthrough to the host's shell.
    '''
    def __init__(self) -> None:
        super().__init__()

    def run(
        self,
        cmds: List[str],
        echo: bool = True,
        capture: bool = False,
        verbose: bool = True
    ) -> List[str]:
        # Note that we use this strategy instead of just running the
        # provided command so that quoting and escape requirements are
        # consistent across activators.
        cmdstr = F"{constants.BASH_MAGIC} {' '.join(cmds)}"
        runargs = {
            'verbatim': True,
            'echo': echo,
            'capture': capture,
            'verbose': verbose
        }
        return host.run(cmdstr, **runargs)

    def set_img_path(self, img_path: str) -> None:
        # Nothing to do.
        pass

    def requires_img_activation(self) -> bool:
        # This activator does not require image activation.
        return False

    def tar2dirs(self, src: str, dst: str) -> str:
        # Nothing to do here.
        return ''

# vim: ft=python ts=4 sts=4 sw=4 expandtab
