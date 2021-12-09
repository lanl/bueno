#
# Copyright (c)      2021 Triad National Security, LLC
#                         All rights reserved.
#
# This file is part of the bueno project. See the LICENSE file at the
# top-level directory of this distribution for more information.
#

'''
Test 1 for experiment.readgs().
'''

from bueno.public import experiment
from bueno.public import logger


def main(argv):
    '''
    main()
    '''
    experiment.name('readgs-test')
    # Program description
    desc = 'Test for experiment.readgs()'
    # Default argument values. Note that one can build up a completely custom
    # collection of run script arguments, but this will setup commonly used
    # arguments that may be useful for many applications.

    # These are default values that can be overwritten by either the input file
    # or command-line arguments passed to the run script. Note that command-line
    # arguments have the highest precedence.
    defaults = experiment.DefaultCLIConfiguration.Defaults
    defaults.csv_output = 'data0.csv'
    defaults.description = desc
    defaults.name = str(experiment.name())
    defaults.executable = 'path-to-exe'
    defaults.input = 'readgs.input'
    # Initial configuration
    config = experiment.DefaultCLIConfiguration(desc, argv, defaults)
    # Parse provided arguments
    config.parseargs()
    for genspec in experiment.readgs(config.args.input, config):
        logger.log(F'name:        {config.args.name}')
        logger.log(F'description: {config.args.description}')
        logger.log(F'executable:  {config.args.executable}')
        logger.log(F'input:       {config.args.input}')
        logger.log(F'csv_output:  {config.args.csv_output}')
        # We can perform 'genspec' substitutions as necessary.
        logger.log('')
        logger.log(F'genspec: {genspec}')
        numpes = range(1, 4)
        cmds = experiment.generate(
            genspec,
            numpes,
            [config.args.executable] * len(numpes)
        )
        for cmd in cmds:
            logger.log(F'Generated Command: {cmd}')
        logger.log('=' * 70)

# vim: ft=python ts=4 sts=4 sw=4 expandtab
