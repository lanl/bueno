#
# Copyright (c)      2019 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Core container image infrastructure.
'''

from bueno.core import metacls

from bueno.public import shell

from abc import ABC, abstractmethod

import os


class ImageActivatorFactory:
    '''
    The container image activator factory.
    '''
    # Modify this list as image activators change.
    # TODO(skg) Add self-registration.
    items = [
        ('charliecloud', lambda x: CharlieCloudImageActivator(x)),
        ('none', lambda x: NoneImageActivator(x))
    ]

    @staticmethod
    def available():
        '''
        Returns list of available container names.
        '''
        return [i[0] for i in ImageActivatorFactory.items]

    @staticmethod
    def known(sname):
        '''
        Returns a boolean indicating whether or not the provided container name
        is known (i.e., recognized) by bueno.
        '''
        return sname in ImageActivatorFactory.available()

    @staticmethod
    def build(activator_name, imgp):
        try:
            aidx = ImageActivatorFactory.available().index(activator_name)
        except Exception:
            ers = 'Unknown container image activator requested: {}'
            raise RuntimeError(ers.format(activator_name))
        # Initialize the activator singleton with the proper implementation.
        Activator(ImageActivatorFactory.items[aidx][1](imgp))


class BaseImageActivator(ABC):
    '''
    Abstract base class for container image activators.
    '''
    def __init__(self, imgp):
        super().__init__()
        # Image path.
        self.imgp = imgp
        if not os.path.isdir(self.imgp):
            ers = 'Invalid container image path provided: {}'
            raise RuntimeError(ers.format(self.imgp))

    @abstractmethod
    def run(self, cmd, echo=True, capture=False, verbose=True):
        '''
        Runs the specified command in a container. By default the executed
        command is emitted echoed before its execution.
        '''
        pass


class CharlieCloudImageActivator(BaseImageActivator):
    '''
    The CharlieCloud image activator.
    '''
    def __init__(self, imgp):
        super().__init__(imgp)

        self.runcmd = 'ch-run'

        inyp = 'Is it in your PATH?\n'
        notf = "'{}' not found. " + inyp

        if not shell.which(self.runcmd):
            errs = notf.format(self.runcmd)
            raise RuntimeError(errs)

    def run(self, cmd, echo=True, capture=False, verbose=True):
        cmds = '{} {} -- {} {}'.format(
            self.runcmd,
            self.imgp,
            # The magic from https://stackoverflow.com/questions/1711970
            # makes cmd quoting a non-issue. Pretty slick... Notice that this is
            # a slightly modified version to meet our needs.
            'bash -c \'${0} ${1+$@}\'',
            cmd
        )

        return shell.run(cmds, echo=echo, capture=capture, verbose=verbose)


class NoneImageActivator(BaseImageActivator):
    '''
    The non-image-activator activator. Just a passthrough to the host's shell.
    '''
    def __init__(self, imgp):
        super().__init__(imgp)

    def run(self, cmd, echo=True, capture=False, verbose=True):
        return shell.run(cmd, echo=echo, capture=capture, verbose=verbose)


class Activator(metaclass=metacls.Singleton):
    '''
    Image activator singleton.
    '''
    def __init__(self, imgactvtr):
        self.imgactvtr = imgactvtr

    @property
    def impl(self):
        return self.imgactvtr
