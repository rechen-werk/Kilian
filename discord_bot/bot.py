"""
    File name: bot.py
    Author: Adrian Vinojcic
    This part is responsible for all stuff related to the discord api.
"""

import discord
from discord.ext import commands

def init_slashcommands():
    print("initializing")


def start(token: str):
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.default())
    bot.run(token)
