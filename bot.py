"""
    File name: bot.py
    Author: Adrian Vinojcic
    This part is responsible for all stuff related to the discord api.
"""

import discord
from discord.ext import commands

import kusss


def init_slashcommands():
    print("initializing")


def start(token: str):
    token, content = kusss.calendar("https://www.kusss.jku.at/kusss/published-calendar.action?token=DRKoIE4v-D2WudkOWr-T5o52DsrPA4TLfoZYLyYP&lang=en")
    bot = commands.Bot(command_prefix=".", intents=discord.Intents.default())
    bot.run(token)
