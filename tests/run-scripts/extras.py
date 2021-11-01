'''
bueno extras test
'''

from bueno.public import experiment
from bueno.public import data
from bueno.public import utils

try:
    import extramod
    from extrapackage import extrapackmod
except ImportError:
    pass
else:
    # Because bueno cannot easily determine what extra stuff was imported at
    # run-time, add the extras by hand to our run's data.
    data.add_asset(data.PythonModuleAsset(extramod))
    data.add_asset(data.PythonModuleAsset(extrapackmod))


def main(_):
    '''
    main()
    '''
    experiment.name('hello-extras-test')
    # Use the extra modules we specified at run-time if they are loaded.
    if utils.module_imported('extramod'):
        extramod.say_hello()
    else:
        raise RuntimeError('*** extramod is not imported ***')

    if utils.module_imported('extrapackage'):
        extrapackmod.say_hello()
    else:
        raise RuntimeError('*** extrapackmod is not imported ***')
