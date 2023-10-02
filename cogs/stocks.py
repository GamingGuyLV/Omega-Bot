import discord
from discord import guild_only, Embed, Colour
from discord.ext import commands, tasks
from discord.commands import Option
import sqlite3
import datetime
import asyncio
import yfinance

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


stocks = []
stock_options = ["TSLA","PYPL","GOOGL","AMZN","NVDA","AMD","MSFT","AAPL","NFLX","INTC"]

con = sqlite3.connect("main.db")
cur = con.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS stocks (
        discordID INT NOT NULL UNIQUE,

        TSLA INT NOT NULL,
        PYPL INT NOT NULL,
        GOOGL INT NOT NULL,
        AMZN INT NOT NULL,
        NVDA INT NOT NULL,
        AMD INT NOT NULL,
        MSFT INT NOT NULL,
        AAPL INT NOT NULL,
        NFLX INT NOT NULL,
        INTC INT NOT NULL,
            
        profit REAL NOT NULL,

        PRIMARY KEY("discordID")
    )''')


stocks_group = discord.SlashCommandGroup(name="stocks", description="All stock commands")


async def updatestocks():
    global stocks
    stocks = []
    tickers = yfinance.Tickers('TSLA PYPL GOOGL AMZN NVDA AMD MSFT AAPL NFLX INTC')
    for item in tickers.tickers.values():
        download = item.info
        stock = {}
        
        stock["Name"] = download.get("longName")
        stock["Abreviation"] = download.get("symbol")
        stock["Price"] = round(download.get("currentPrice"), 2)

        stocks.append(stock)

    ttime = datetime.datetime.now()
    time = ttime.strftime("%Y-%m-%d %H:%M:%S - ")
    
    print(f"{bcolors.OKBLUE}{time}[Stocks] Stocks updated!{bcolors.ENDC}")
    

async def get_owned_stocks(ctx: discord.AutocompleteContext):
    cur.execute(f'''SELECT * FROM stocks WHERE discordID={ctx.interaction.user.id}''')
    fetched = cur.fetchone()
    owned = []
    if fetched:
        TSLA, PYPL, GOOGL, AMZN, NVDA, AMD, MSFT, AAPL, NFLX, INTC = int(fetched[1]), int(fetched[2]), int(fetched[3]), int(fetched[4]), int(fetched[5]), int(fetched[6]), int(fetched[7]), int(fetched[8]), int(fetched[9]), int(fetched[10])

    if TSLA >= 1:
        owned.append("TSLA")
    if PYPL >= 1:
        owned.append("PYPL")
    if GOOGL >= 1:
        owned.append("GOOGL")
    if AMZN >= 1:
        owned.append("AMZN")
    if NVDA >= 1:
        owned.append("NVDA")
    if AMD >= 1:
        owned.append("AMD")
    if MSFT >= 1:
        owned.append("MSFT")
    if AAPL >= 1:
        owned.append("AAPL")
    if NFLX >= 1:
        owned.append("NFLX")
    if INTC >= 1:
        owned.append("INTC")

    return owned

async def get_owned_stocks_amount(ctx: discord.AutocompleteContext):
    cur.execute(f'''SELECT {ctx.options['stock']} FROM stocks WHERE discordID={ctx.interaction.user.id}''')
    fetched = cur.fetchone()
    if fetched:
        amount = fetched[0]

    owned = []

    for x in range(1, amount+1):
        owned.append(str(x))
        
    
    return owned



class Stocks(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.updatestocksloop.start()

    def cog_unload(self):
        self.updatestocksloop.cancel()

    @stocks_group.command(name="view", description="Look at the current(updates every hour) stock prices!") # View
    @guild_only()
    async def view(ctx):
        embed = Embed(colour=Colour.purple())
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        if len(stocks) <= 1:
            embed.add_field(name=f"Stocks have not been loaded...", value=f"Sorry for inconvenience.")

        for stock in stocks:
            embed.add_field(name=f"{stock['Abreviation']} : {stock['Name']}", value=f"`${stock['Price']}`", inline=False)

        await ctx.respond(embed=embed)


    @stocks_group.command(name="buy", description="Buy some stocks!") # Buy
    @guild_only()
    async def buy(ctx, stock: Option(str, "Which stock?", choices=stock_options, required=True), amount: Option(int, "How many will you buy?", required=True)):
        await ctx.defer()

        cur.execute(f'''SELECT balance FROM users WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            balance = round(float(fetched[0]), 2)
        else:
            balance = 100
            cur.execute(f'''INSERT INTO users (discordID, balance, inventory, stocks, winnings, losses, games_played, amount_bet_in_games, stolen, stolen_from, prestige) VALUES ({int(ctx.author.id)}, 100, "Empty", "Empty", 0.0, 0.0, 0, 0.0, 0.0, 0.0, "None")''')
            con.commit()


        cur.execute(f'''SELECT {stock}, profit FROM stocks WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            owned = int(fetched[0])
            profit = fetched[1]
        else:
            cur.execute(f'''INSERT INTO stocks (discordID, TSLA, PYPL, GOOGL, AMZN, NVDA, AMD, MSFT, AAPL, NFLX, INTC, profit) VALUES ({int(ctx.author.id)},0,0,0,0,0,0,0,0,0,0,0.0)''')
            con.commit()
            owned = 0
            profit = 0

        
        for stocky in stocks:
            if stocky['Abreviation'] == stock:
                price = stocky['Price']
                break

        priceAll = round(amount * price, 2)

        if balance < priceAll:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name="Stocks", value=f"Your balance is too low to afford that. You have: `${balance}` , it costs: `${priceAll}`")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
            await ctx.respond(embed=embed)
            return


        newbalance = round(balance - priceAll, 2)
        owned += amount
        profit = round(profit - priceAll, 2)

        cur.execute(f'''UPDATE users SET balance={newbalance} WHERE discordID={int(ctx.author.id)}''')
        cur.execute(f'''UPDATE stocks SET {stock}={owned}, profit={profit} WHERE discordID={int(ctx.author.id)}''')
        con.commit()

        embed = Embed(colour=Colour.purple())
        embed.add_field(name="Stocks", value=f"You've bought **{amount} of {stock}** for `${priceAll}`. Remaining balance: ```py\n${newbalance}```")
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)


    @stocks_group.command(name="sell", description="Sell before it's too late!") # Sell
    @guild_only()
    async def sell(ctx, stock: Option(str, autocomplete=discord.utils.basic_autocomplete(get_owned_stocks), required=True), amount: Option(int, autocomplete=discord.utils.basic_autocomplete(get_owned_stocks_amount), required=True)):
        await ctx.defer()

        cur.execute(f'''SELECT balance FROM users WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            balance = round(float(fetched[0]), 2)
        else:
            balance = 100
            cur.execute(f'''INSERT INTO users (discordID, balance, inventory, stocks, winnings, losses, games_played, amount_bet_in_games, stolen, stolen_from, prestige) VALUES ({int(ctx.author.id)}, 100, "Empty", "Empty", 0.0, 0.0, 0, 0.0, 0.0, 0.0, "None")''')
            con.commit()


        cur.execute(f'''SELECT {stock}, profit FROM stocks WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            owned = int(fetched[0])
            profit = fetched[1]
        else:
            cur.execute(f'''INSERT INTO stocks (discordID, TSLA, PYPL, GOOGL, AMZN, NVDA, AMD, MSFT, AAPL, NFLX, INTC) VALUES ({int(ctx.author.id)},0,0,0,0,0,0,0,0,0,0)''')
            con.commit()
            owned = 0
            profit = 0


        for stocky in stocks:
            if stocky['Abreviation'] == stock:
                price = stocky['Price']
                break

        priceAll = round(amount * price, 2)
        profit = round(profit + priceAll, 2)
        owned -= amount

        newbalance = round(balance + priceAll, 2)

        cur.execute(f'''UPDATE users SET balance={newbalance} WHERE discordID={int(ctx.author.id)}''')
        cur.execute(f'''UPDATE stocks SET {stock}={owned}, profit={profit} WHERE discordID={int(ctx.author.id)}''')
        con.commit()

        embed = Embed(colour=Colour.purple())
        embed.add_field(name="Stocks", value=f"You've sold **{amount} of {stock}** for `${priceAll}`. Current overall profit is: ```py\n${profit}``` \nNew balance: ```py\n${newbalance}```")
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)


    @stocks_group.command(name="owned", description="Check on your stocks!") # Owned
    @guild_only()
    async def owned(ctx):
        await ctx.defer()

        embed = Embed(colour=Colour.purple())
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        worth = 0

        cur.execute(f'''SELECT * FROM stocks WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            x = 1
            for stock in stocks:
                if fetched[x] >= 1:
                    embed.add_field(name=f"{stock['Abreviation']} : {stock['Name']}", value=f"`{fetched[x]}`", inline=False)

                    worth += round(stock['Price'] * fetched[x], 2)

                x += 1

        embed.add_field(name=f"\nWorth", value=f"Your total worth of stocks with current prices is: ```py\n${worth}```")

        await ctx.respond(embed=embed)


















    @tasks.loop(minutes=60)
    async def updatestocksloop(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)
    
        await updatestocks()


def setup(bot):
    bot.add_application_command(stocks_group)
    bot.add_cog(Stocks(bot))