"""
    File name: kilian.py
    Author: Adrian Vinojcic
    This part is responsible for everything related to the discord api.
"""

import argparse
import interactions
import kusss as uni


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--token",
        type=str,
        required=False,
        dest='token',
        help="Provide the Discord Bot Token as string."
    )
    return parser.parse_args()


def read_token_file():
    with open("secrets", 'r') as f:
        return f.readlines()[0].strip()


if __name__ == '__main__':
    args = parse_args()
    bot_token = args.token if args.token is not None else read_token_file()

    bot = interactions.Client(token=bot_token)

    @bot.command()
    @interactions.option(description="Provide the calendar link from KUSSS here.")
    async def kusss(ctx: interactions.CommandContext, link: str):
        """Take advantage of the features provided by Kilian™."""
        user_token = uni.token(link)
        courses = uni.courses(link)
        s = ""
        for course in courses:
            s += course.name + "\n"
        await ctx.send(s)

    bot.start()
