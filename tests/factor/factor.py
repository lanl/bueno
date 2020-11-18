'''
factor.py
    written by Jacob Dickens, Nov 2020

    Basic principle:
        Given some integer N, find a, b, c such that
        N = a * b * c where a, b and c are as close
        in value as is possible.
'''

import argparse
import typing


def parse_args() -> argparse.Namespace:
    '''
    Process program arguments
    '''
    parser = argparse.ArgumentParser('')
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
        raise argparse.ArgumentTypeError(F"{args.num} isn't a positive int")

    return args


class Factor:
    '''
    Provide tools for prime factor combination and
    intellegent recombination
    '''

    def __init__(self, number: int, dimensions: int):
        '''
        Initialize factor instance as specified
        '''
        self.number = number
        self.dimensions = dimensions
        self.factor_list: typing.List[int] = []
        self.prime_list = [
            2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
            61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131,
            137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197,
            199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271,
            277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353,
            359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433,
            439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509,
            521, 523, 541
        ]  # First 100 primes

    def get_prime(self, number: int) -> None:
        '''
        Fill factor_list with prime factors
        '''
        print(F'{number} -> {self.factor_list}')

        if number in self.prime_list:
            self.factor_list.append(number)
            return  # Is prime; done.

        for value in range(2, int(number/2) + 1):
            if number % value != 0:
                continue  # Not clean division; try next.

            # else, value cleanly divides number
            # append prime factor, repeat with remainder
            self.factor_list.append(value)
            self.get_prime(int(number/value))
            break

    def validate_list(self) -> None:
        '''
        Check factor list total
        '''
        product = 1
        for item in self.factor_list:
            product *= item

        # append unlisted prime if missing
        if self.number != product:
            remainder = int(self.number/product)
            print(F'{self.number} != {product}')
            print(F'Appending {remainder}')
            self.factor_list.append(remainder)

        else:
            print(F'{self.number} == {product}\nValid!')

    @staticmethod
    def get_root(degree: int, number: int) -> float:
        '''
        Determine the degree root of number
        (nth root of x)
        '''
        return number ** (1.0 / degree)

    def condense_list(self) -> None:
        '''
        Condense factor list to desired dimensions
        '''
        temp_list = self.factor_list
        length = len(temp_list)

        while length > self.dimensions:
            print(temp_list)

            # Case 1: List is 1 item too long
            # Combine the first 2 items
            if length == (self.dimensions + 1):
                print('Case 1 -> ', end='')

                alyx = temp_list[0] * temp_list[1]
                temp_list = temp_list[2:]
                temp_list.insert(0, alyx)

                self.factor_list = temp_list
                return  # Done

            # Check for large values
            contains_large = False
            large_val = 0
            for item in temp_list:
                if item >= Factor.get_root(self.dimensions, self.number):
                    contains_large = True
                    large_val = item

            # Case 2: List contains a large value
            # Combine first and second largest
            if contains_large:
                print('Case 2 -> ', end='')

                breen = temp_list[0] * temp_list[length - 2]
                temp_list = temp_list[1:-2]
                temp_list.append(breen)
                temp_list.append(large_val)

                length -= 1

            # Case 3: List is mostly even distribution
            # Combine first and last items
            else:
                print('Case 3 -> ', end='')

                calhoun = temp_list[0] * temp_list[length - 1]
                temp_list = temp_list[1:-1]
                temp_list.append(calhoun)

                length -= 1

        # End of while
        # Factor list is <= desired dimension
        if length < self.dimensions:
            buffer = [1] * self.dimensions
            temp_list.extend(buffer)  # Extend to dimension length
            temp_list = temp_list[0: self.dimensions]

        self.factor_list = temp_list
        return  # Done


def evaluate(num: int, dim: int) -> typing.List[int]:
    '''
    Perform factor calculations
    '''
    # Get prime factors
    # Validate factor list
    # Recombine factor list
    # Sort factor list (Greatest-Least)

    breakdown = Factor(num, dim)
    print('\nFactoring...')
    breakdown.get_prime(num)

    print('\nValidating prime factors...')
    breakdown.validate_list()

    print('\nCondensing factor list...')
    breakdown.condense_list()

    breakdown.factor_list.sort(reverse=True)
    print(F'\nFinal: {breakdown.factor_list}')

    return breakdown.factor_list


def main() -> None:
    '''
    Main program
    '''
    param = parse_args()
    evaluate(param.num, param.dim)


if __name__ == '__main__':
    main()
