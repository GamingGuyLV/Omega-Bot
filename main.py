# nuitka --onefile --include-plugin-dir=cogs --output-dir=dist --python-flag=-O  main.py

import os
import discord


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


bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"{bcolors.FAIL}---------------------------------------------------{bcolors.ENDC}")
    print(f"{bcolors.OKCYAN}Logged in as {bot.user}{bcolors.ENDC}")
    print(f"{bcolors.OKCYAN}Bot ID: {bot.user.id}{bcolors.ENDC}")
    print(f"{bcolors.FAIL}---------------------------------------------------{bcolors.ENDC}")


### Gambling -----------------------
bot.load_extension("cogs.gambling")

### Farming -----------------------
bot.load_extension("cogs.farming")

### Stocks -----------------------
bot.load_extension("cogs.stocks")

### Work -----------------------
bot.load_extension("cogs.work")

### Events -----------------------
bot.load_extension("cogs.events")


bot.run("MTEzMTYzNTQ4NDg0NjczNTQ4MA.GCtDnY.5tuLM9P8DVXNIBciD3_GLgnSDtPsbeX6SYrLFI")