import discord
from discord import guild_only, Embed, Colour
from discord.ext import commands, tasks
from discord.commands import Option
import random
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




class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"This command is on a {round(error.retry_after, 2)}sec cooldown for you!", ephemeral=True)
            return





def setup(bot):
    bot.add_cog(Events(bot))