'''
factor.py
    written by Jacob Dickens, Nov 2020

    Basic principle:
        Given some integer N, find a, b, c such that
        N = a * b * c where a, b and c are as close
        in value as is possible.
'''

import argparse

from bueno.public import experiment


def parse_args() -> argparse.Namespace:
    '''
    Process program arguments
    '''
    parser = argparse.ArgumentParser('Test experiment factor usage')
    parser.add_argument(
        'num',
        type=int,
        help='Original number'
    )
    parser.add_argument(
        '--dim',
        type=int,
        default=3,
        help='Dimensions'
    )

    args = parser.parse_args()
    if args.num < 1:
        raise argparse.ArgumentTypeError(F"{args.num} isn't a positive int!")

    if args.dim < 1:
        raise argparse.ArgumentTypeError(F"{args.dim} isn't a positive int")

    return args


def main() -> None:
    '''
    Main program
    '''
    param = parse_args()
    result = experiment.evaluate_factors(param.num, param.dim)
    print(result)


if __name__ == '__main__':
    main()
