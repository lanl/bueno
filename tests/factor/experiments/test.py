'''
test.py
    written by Jacob Dickens Nov, 2020

    Generate a range of numbers between 10 and user cap
    and iteratively call factor.py for testing.
    Save data for postrun analysis.
'''

import argparse
import subprocess
import csv


def parse_args() -> argparse.Namespace:
    '''
    Process program arguments
    '''
    parser = argparse.ArgumentParser('')
    parser.add_argument(
        'roof',
        type=int,
        help='Test value ceiling'
    )
    parser.add_argument(
        '--dim',
        type=int,
        help='Final factor count',
        default=3
    )
    parser.add_argument(
        '--floor',
        type=int,
        help='Test value floor',
        default=10
    )

    args = parser.parse_args()
    if args.roof < 10:
        raise argparse.ArgumentTypeError(F'{args.roof} must be > 10!')

    if args.dim < 2:
        raise argparse.ArgumentTypeError(F'{args.dim} must be > 1!')

    if args.floor < 10:
        raise argparse.ArgumentTypeError(F'{args.floor} must be >= 10!')

    if args.floor >= args.roof:
        raise argparse.ArgumentTypeError('Test value range invalid!')

    return args


class Experiment:
    '''
    Define experiment parameters when testing factor.py
    '''
    def __init__(self, ceiling: int, dimensions: int, floor: int):
        self.roof = ceiling
        self.dim = dimensions
        self.floor = floor

    def run_tests(self) -> None:
        '''
        Call factor.py with data list
        '''
        with open('data.csv', 'wt') as data_file:
            # Setup csv writer and add row header
            csv_writer = csv.writer(data_file)
            header = ['Original', 'Factors']
            csv_writer.writerow(header)

            # Run subprocess experiments
            # Recording output for csv data file
            for value in range(self.floor, self.roof + 1):
                process_info = subprocess.run(
                    F'python ../factor.py {value} --dim {self.dim}',
                    shell=True,
                    capture_output=True
                )

                # Fetch final output from factor.py
                # Format to output to string
                output = process_info.stdout.decode('utf-8')
                result = output.split('\n')[-2][8:-1]  # Trim output
                print(F'{value} -> {result}')

                # Create csv data entry
                row = [value]
                for factor in result.split(', '):
                    row.append(int(factor))
                csv_writer.writerow(row)


def main() -> None:
    '''
    Main program
    '''
    params = parse_args()
    exp = Experiment(params.roof, params.dim, params.floor)
    exp.run_tests()


if __name__ == '__main__':
    main()
