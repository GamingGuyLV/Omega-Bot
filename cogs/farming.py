import discord
from discord import guild_only, Embed, Colour
from discord.ext import commands, tasks
from discord.commands import Option
import random
import sqlite3
import datetime
import asyncio


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

con = sqlite3.connect("main.db")
cur = con.cursor()


farming_group = discord.SlashCommandGroup(name="farming", description="All farming commands")


class Farming(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

     






def setup(bot):
    bot.add_application_command(farming_group)
    bot.add_cog(Farming(bot))