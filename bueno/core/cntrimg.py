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
    # TODO(skg) Use lambdas for instance creation?
    items = [
        'charliecloud'
    ]

    @staticmethod
    def available():
        '''
        Returns list of available container names.
        '''
        return ImageActivatorFactory.items

    @staticmethod
    def known(sname):
        '''
        Returns a boolean indicating whether or not the provided container name
        is known (i.e., recognized) by bueno.
        '''
        return sname in ImageActivatorFactory.items

    @staticmethod
    def build(activator_name, imgp):
        actvtr = None
        if activator_name == 'charliecloud':
            actvtr = CharlieCloudImageActivator(imgp)
        else:
            ers = 'Unknown container image activator requested: {}'
            raise RuntimeError(ers.format(activator_name))
        # Initialize the activator singleton with the proper implementation.
        Activator(actvtr)


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
    def run(self, cmd):
        '''
        Runs the specified command in a container.
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

    def run(self, cmd):
        cmds = '{} {} -- {} "{}"'.format(
            self.runcmd,
            self.imgp,
            # The magic from https://stackoverflow.com/questions/1711970
            # makes cmd quoting a non-issue. Pretty slick...
            'bash -c \'${0} ${1+"$@"}\'',
            cmd
        )
        shell.run(cmds)


class Activator(metaclass=metacls.Singleton):
    '''
    Image activator singleton.
    '''
    def __init__(self, imgactvtr):
        self.imgactvtr = imgactvtr

    def impl(self):
        return self.imgactvtr
