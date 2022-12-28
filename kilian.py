"""
    File name: kilian.py
    Author: Adrian Vinojcic
    This part is responsible for config and argument parsing as well as providing the necessary information to the bot.
"""

import argparse
import discord_bot.bot as kilian


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token",
        type=str,
        required=False,
        dest='token',
        help="Provide the Discord Bot Token as string."
    )
    parser.add_argument(
        "-i",
        action="store_true",
        help="Initialize the slash commands(only necessary on first startup)."
    )
    return parser.parse_args()


def read_token_file():
    with open("secret", 'r') as f:
        return f.readlines()[0].strip()


if __name__ == '__main__':
    args = parse_args()
    if args.i:
        kilian.init_slashcommands()
    kilian.start(args.token if args.token is not None else read_token_file())
