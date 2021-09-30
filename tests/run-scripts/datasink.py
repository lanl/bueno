'''
datasink tests
'''

from bueno.public import datasink
from bueno.public import experiment


def main(_):
    '''
    main()
    '''
    experiment.name('datasink-test')

    metrics = ['A Data', 'B Data', 'C Data']

    data = {
        'a': [1, 2, 3],
        'b': [10000000000, 0.1, 3e2],
        'c': ['-1', 10, 'str']
    }

    tdata = zip(
        data['a'],
        data['b'],
        data['c']
    )

    table = datasink.Table()
    table.addrow(metrics, withrule=True)
    for row in tdata:
        table.addrow(row)
    table.emit()
