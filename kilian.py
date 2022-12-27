"""
    File name: kilian.py
    Author: Adrian Vinojcic
"""

import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token",
        type=str,
        required=False,
        dest='token',
        help="Provide the Discord Bot Token as token."
    )
    parser.add_argument(
        "-i",
        action="store_true",
        help="Initialize the slash commands(only necessary on first startup."
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    print(args.token)
    print(args.i)
# TODO: implement a file where the config can be defaulted into
