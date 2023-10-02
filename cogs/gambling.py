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

blackjack_decks = {}

# --------------------------------- Users
cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        discordID INT NOT NULL UNIQUE,

        balance REAL NOT NULL,

        inventory STRING NOT NULL,
        stocks STRING NOT NULL,

        winnings REAL NOT NULL,
        losses REAL NOT NULL,

        games_played INT NOT NULL,
        amount_bet_in_games REAL NOT NULL,

        stolen REAL NOT NULL,
        stolen_from REAL NOT NULL,

        prestige STR NOT NULL,

        PRIMARY KEY("discordID")
    )''')

# --------------------------------- Stats

# --------- Blackjack
cur.execute('''
    CREATE TABLE IF NOT EXISTS blackjack_stats (
        discordID INT NOT NULL UNIQUE, 

        blackjack_played INT NOT NULL,
        blackjack_won INT NOT NULL,
        blackjack_lost INT NOT NULL,
        blackjack_bets REAL NOT NULL,
        blackjack_winnings REAL NOT NULL,
        blackjack_losses REAL NOT NULL,
        blackjack_hits INT NOT NULL,
        blackjack_stands INT NOT NULL,
        blackjack_doubledown INT NOT NULL,

        PRIMARY KEY("discordID")
    )''')

# --------- Coinflip
cur.execute('''
    CREATE TABLE IF NOT EXISTS coinflip_stats (
        discordID INT NOT NULL UNIQUE,

        coinflip_played INT NOT NULL,
        coinflip_won INT NOT NULL,
        coinflip_lost INT NOT NULL,
        coinflip_bets REAL NOT NULL,
        coinflip_winnings REAL NOT NULL,
        coinflip_losses REAL NOT NULL,
        coinflip_heads INT NOT NULL,
        coinflip_tails INT NOT NULL,

        PRIMARY KEY("discordID")
    )''')

# ---------- Chances
cur.execute('''
    CREATE TABLE IF NOT EXISTS chances_stats (
        discordID INT NOT NULL UNIQUE,

        chances_played INT NOT NULL,
        chances_won INT NOT NULL,
        chances_lost INT NOT NULL,
        chances_bets REAL NOT NULL,
        chances_winnings REAL NOT NULL,
        chances_losses REAL NOT NULL,

        PRIMARY KEY("discordID")
    )''')

# ----------- Roulette
cur.execute('''
    CREATE TABLE IF NOT EXISTS roulette_stats (
        discordID INT NOT NULL UNIQUE,

        roulette_played INT NOT NULL,
        roulette_won INT NOT NULL,
        roulette_lost INT NOT NULL,
        roulette_bets REAL NOT NULL,
        roulette_winnings REAL NOT NULL,
        roulette_losses REAL NOT NULL,
        roulette_red INT NOT NULL,
        roulette_black INT NOT NULL,
        roulette_odd INT NOT NULL,
        roulette_even INT NOT NULL,
        roulette_high INT NOT NULL,
        roulette_low INT NOT NULL,
        roulette_1st12 INT NOT NULL,
        roulette_2nd12 INT NOT NULL,
        roulette_3rd12 INT NOT NULL,
        roulette_zero INT NOT NULL,

        PRIMARY KEY("discordID")
    )''')


async def checkbalance(ctx, amount):
    check = True

    cur.execute(f'''SELECT balance FROM users WHERE discordID={int(ctx.author.id)}''')
    fetched = cur.fetchone()
    if fetched:
        balance = round(float(fetched[0]), 2)
    else:
        balance = 100
        cur.execute(f'''INSERT INTO users (discordID, balance, inventory, stocks, winnings, losses, games_played, amount_bet_in_games, stolen, stolen_from, prestige) VALUES ({int(ctx.author.id)}, 100, "Empty", "Empty", 0.0, 0.0, 0, 0.0, 0.0, 0.0, "None")''')
        con.commit()


    if amount <= 0:
        embed = Embed(colour = Colour.red())
        embed.add_field(name="Balance Check", value="A bet can't be zero or negative :/")
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)

        check = False
        return
    
    if balance < amount:
        embed = Embed(colour = Colour.red())
        embed.add_field(name="Balance Check", value=f"Insufficient balance... :/")
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)

        check = False
        return
    
    return check, balance


gambling_group = discord.SlashCommandGroup(name="gambling", description="All gambling commands")
economics_group = discord.SlashCommandGroup(name="econ", description="Consider economics")
stats_group = discord.SlashCommandGroup(name="stats", description="Admire your failures")


class Gambling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.statroundup.start()

    def cog_unload(self):
        self.statroundup.cancel()


    @gambling_group.command(name="help", description="Help about all this bs") # Help
    @guild_only()
    async def help(ctx):
        await ctx.defer()

        embed = Embed(colour=Colour.purple())
        embed.set_author(name=f"Gambling help")
        embed.add_field(name=f"/econ balance `member`", value=f"Check yours, or someone elses' balance.", inline=False) # Econ Balance
        embed.add_field(name=f"/econ leaderboard", value=f"Sends a Top 10 leaderboard by balance. Brag to your friends, compete for first place!", inline=False) # Econ Leaderboard
        embed.add_field(name=f"/gambling coinflip `bet` `option`", value=f"Gamble away your money with a coinflip. Place your bet and choose heads or tails!", inline=False) # Gambling Coinflip
        embed.add_field(name=f"/gambling blackjack `bet`", value=f"Play a cheeky card game for money. DoubleDown doubles your bet(if you can afford that) and gives you a single card. Hope you don't go over 21!", inline=False) # Gambling Blackjack
        embed.add_field(name=f"/gambling chances `bet` `chance`", value=f"A game of chance as the name implies. The higher your chances of winning, the lower the reward, it's that simple!", inline=False) # Gambling Chances
        embed.add_field(name=f"/gambling roulette `bet` `slot`", value=f"Regular game of roulette, you bet on a slot and hope to win! 50/50 slots double your bet, 33/66 slots triple it and 0 multiplies it by 35! I'll be impressed if you actually land a 0 while betting on it.", inline=False) # Gambling Roulette
        embed.add_field(name=f"/stats coinflip `member`", value=f"Get dissapointed in your luck with a coin. Also check how miserable your comrades are!", inline=False) # Stats Coinflip
        embed.add_field(name=f"/stats blackjack `member`", value=f"HOW MUCH DID YOU GAMBLE AWAY IN BLACKJACK? THATS OUR MORTGAGE JHONNY!", inline=False) # Stats Blackjack
        embed.add_field(name=f"/stats chances `member`", value=f"What are the chances you actually made a profit?", inline=False) # Stats Chances
        embed.add_field(name=f"/stats roulette `member`", value=f"Maybe with this you can predict where the ball will land next, i for sure can't.", inline=False) # Stats Roulette
        embed.add_field(name=f"Statistic updates", value=f"Every 5 minutes your stats across all games get rounded up into your personal `overall` stats. Command for those is not finished yet, but when it is, you'll know why it doesn't update immediatly.", inline=False) # Stat Update
        
        await ctx.respond(embed=embed)

    
    @economics_group.command(name="balance", description="Check your or someone elses' balance.") # ---------------- Balance
    @guild_only()
    async def balance(ctx, member: Option(discord.Member, description="Member (Empty if yourself)", default="", required=False)):
        if member == "":
            member = ctx.author


        cur.execute(f'''SELECT balance FROM users WHERE discordID={int(member.id)}''')
        fetched = cur.fetchone()
        if fetched:
            balance = round(float(fetched[0]), 2)
        else:
            balance = 100
            cur.execute(f'''INSERT INTO users (discordID, balance, inventory, stocks, winnings, losses, games_played, amount_bet_in_games, stolen, stolen_from, prestige) VALUES ({int(ctx.author.id)}, 100, "Empty", "Empty", 0.0, 0.0, 0, 0.0, 0.0, 0.0, "None")''')
            con.commit()


        if member == ctx.author:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name="Balance", value=f"Your balance is: ```py\n${balance}```")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
            await ctx.respond(embed=embed)
        
        else:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name="Balance", value=f"{member.mention} balance is: ```py\n${balance}```")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
            await ctx.respond(embed=embed)


    @economics_group.command(description = "Leaderboard of the top balances!") # ------------ Leaderboard
    @guild_only()
    async def leaderboard(ctx):
        await ctx.defer()
        users = {}

        cur.execute('''SELECT * FROM users ORDER BY balance DESC LIMIT 10''')
        fetched = cur.fetchall()

        embed = Embed(colour=Colour.purple())

        for user in fetched:
            member = await ctx.guild.fetch_member(int(user[0]))
            balance = float(user[1])

            users[member] = balance

        keys = list(users.keys())

        embed.add_field(name="Top 10 richest users by balance!", value=f" 1){keys[0].mention if len(keys) >= 1 else 'Empty'} : **{users[keys[0]] if len(keys) >= 1 else 'Empty'}**\n 2){keys[1].mention if len(keys) >= 2 else 'Empty'} : **{users[keys[1]] if len(keys) >= 2 else 'Empty'}**\n 3){keys[2].mention if len(keys) >= 3 else 'Empty'} : **{users[keys[2]] if len(keys) >= 3 else 'Empty'}**\n 4){keys[3].mention if len(keys) >= 4 else 'Empty'} : **{users[keys[3]] if len(keys) >= 4 else 'Empty'}**\n 5){keys[4].mention if len(keys) >= 5 else 'Empty'} : **{users[keys[4]] if len(keys) >= 5 else 'Empty'}**\n 6){keys[5].mention if len(keys) >= 6 else 'Empty'} : **{users[keys[5]] if len(keys) >= 6 else 'Empty'}**\n 7){keys[6].mention if len(keys) >= 7 else 'Empty'} : **{users[keys[6]] if len(keys) >= 7 else 'Empty'}**\n 8){keys[7].mention if len(keys) >= 8 else 'Empty'} : **{users[keys[7]] if len(keys) >= 8 else 'Empty'}**\n 9){keys[8].display_name if len(keys) >= 9 else 'Empty'} : **{users[keys[8]] if len(keys) >= 9 else 'Empty'}**\n 10){keys[9].mention if len(keys) >= 10 else 'Empty'} : **{users[keys[9]] if len(keys) >= 10 else 'Empty'}**")
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)
            

    # =========================================== Games


    @gambling_group.command(name="coinflip", description="Check your luck with a coinflip!") # Coinflip
    @guild_only()
    async def coinflip(ctx, bet: Option(float, description="How much to bet?", required=True), option: Option(str, description="So what will it be?", choices=["Heads", "Tails"], required=True)):
        await ctx.defer()

        passed, balance = await checkbalance(ctx, bet)

        if not passed:
            return
        
        
        cur.execute(f'''SELECT * FROM coinflip_stats WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if not fetched:
            played, won, lost, bets, winnings, losses, heads, tails = 0, 0, 0, 0, 0, 0, 0, 0
            cur.execute(f'''INSERT INTO coinflip_stats (discordID, coinflip_played, coinflip_won, coinflip_lost, coinflip_bets, coinflip_winnings, coinflip_losses, coinflip_heads, coinflip_tails) VALUES ({int(ctx.author.id)}, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0)''')
            con.commit()
        
        else:
            played, won, lost, bets, winnings, losses, heads, tails = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8]
        

        cur.execute(f'''SELECT earned_unpaid, last_paid FROM work WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            earned_unpaid = float(fetched[0])
            last_paid = int(fetched[1])

        else:
            cur.execute(f'''INSERT INTO work (discordID, math, geography, sports, culture, grammar, history, biology, chemistry, math_questions, geography_questions, sports_questions, culture_questions, grammar_questions, history_questions, biology_questions, chemistry_questions, education_level, profession, salary, correct_questions, failed_questions, earned_total, worked, paid_taxes, lost_to_irs, last_paid, earned_unpaid) VALUES ({int(ctx.author.id)}, 0,0,0,0,0,0,0,0,"0","0","0","0","0","0","0","0","uneducated", "homeless", 0.0, 0,0, 0.0, 0, 0.0, 0.0, 0, 0)''')
            con.commit()

            earned_unpaid = 0
            last_paid = 0


        flip = random.randint(1,2)

        if flip == 1: # Heads
            if option == "Heads": # Won
                newbalance = balance + bet
                won += 1
                bets += bet
                winnings += bet
                heads += 1
                played += 1
                earned_unpaid += bet

                if last_paid == 0:
                    last_paid = round(datetime.datetime.now().timestamp())

                cur.execute(f'''UPDATE coinflip_stats SET coinflip_played={played}, coinflip_won={won}, coinflip_bets={bets}, coinflip_winnings={winnings}, coinflip_heads={heads}''')
                cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                embed = Embed(colour=Colour.purple())
                embed.set_author(name="CoinFlip")
                embed.add_field(name="It's heads! You win!", value=f"Your new balance is: ```py\n${newbalance}```")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                await ctx.respond(embed=embed)
                return
            
            if option == "Tails": # Lost
                newbalance = balance - bet
                lost += 1
                bets += bet
                losses += bet
                tails += 1
                played += 1

                cur.execute(f'''UPDATE coinflip_stats SET coinflip_played={played}, coinflip_lost={lost}, coinflip_bets={bets}, coinflip_winnings={losses}, coinflip_heads={tails}''')
                cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                embed = Embed(colour=Colour.purple())
                embed.set_author(name="CoinFlip")
                embed.add_field(name="It's heads! You lose!", value=f"Your new balance is: ```py\n${newbalance}```")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                await ctx.respond(embed=embed)
                return
            

        if flip == 2: # Tails
            if option == "Heads": # Lost
                newbalance = balance - bet
                lost += 1
                bets += bet
                losses += bet
                heads += 1
                played += 1

                cur.execute(f'''UPDATE coinflip_stats SET coinflip_played={played}, coinflip_lost={lost}, coinflip_bets={bets}, coinflip_winnings={losses}, coinflip_heads={heads}''')
                cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                embed = Embed(colour=Colour.purple())
                embed.set_author(name="CoinFlip")
                embed.add_field(name="It's tails! You lose!", value=f"Your new balance is: ```py\n${newbalance}```")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                await ctx.respond(embed=embed)
                return
            
            if option == "Tails": # Won
                newbalance = balance + bet
                won += 1
                bets += bet
                winnings += bet
                tails += 1
                played += 1
                earned_unpaid += bet

                if last_paid == 0:
                    last_paid = round(datetime.datetime.now().timestamp())

                cur.execute(f'''UPDATE coinflip_stats SET coinflip_played={played}, coinflip_won={won}, coinflip_bets={bets}, coinflip_winnings={winnings}, coinflip_heads={tails}''')
                cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                embed = Embed(colour=Colour.purple())
                embed.set_author(name="CoinFlip")
                embed.add_field(name="It's tails! You win!", value=f"Your new balance is: ```py\n${newbalance}```")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                await ctx.respond(embed=embed)
                return


    @gambling_group.command(name="blackjack", description="Get as close to 21 as you can.") # Blackjack
    @guild_only()
    async def blackjack(ctx, bet : Option(float, description="How much to bet?", required=True)):
        await ctx.defer()

        passed, balance = await checkbalance(ctx, bet)

        if not passed:
            return
                       

        def shuffle(deck):
            if len(deck) <= 8:
                deck = [2,3,4,5,6,7,8,9,10,11,12,13,14]*4
                return deck
            else:
                return deck
            
        def deal(deck):
            hand = []
            for i in range(2):
                random.shuffle(deck)
                card = deck.pop()
                if card == 11:card = "J"
                if card == 12:card = "Q"
                if card == 13:card = "K"
                if card == 14:card = "A"
                hand.append(card)
            return hand
        
        def total(hand):
            total = 0
            for card in hand:
                if card == "J" or card == "Q" or card == "K":
                    total += 10
                
                elif card == "A":
                    if total >= 12: total += 1
                    else: total += 11
                
                else: total += card
            return total
        
        def hit(hand, deck):
            card = deck.pop()
            if card == 11:card = "J"
            if card == 12:card = "Q"
            if card == 13:card = "K"
            if card == 14:card = "A"
            hand.append(card)
            return hand, deck

        deck = blackjack_decks.get(f"{ctx.author.id}")
        moves = []

        if deck == None:
            deck = []
        
        deck = shuffle(deck)

        dealer_hand = deal(deck)
        player_hand = deal(deck)

        hitbutton = discord.ui.Button(label="Hit!", style=discord.ButtonStyle.primary)
        standbutton = discord.ui.Button(label="Stand.", style=discord.ButtonStyle.success)
        doubledownbutton = discord.ui.Button(label="Double Down!!!", style=discord.ButtonStyle.danger)

        view = discord.ui.View()
        view.add_item(hitbutton)
        view.add_item(standbutton)
        view.add_item(doubledownbutton)


        async def hit_callback(interaction):
            if interaction.user == ctx.author:

                cur.execute(f'''SELECT * FROM blackjack_stats WHERE discordID={int(ctx.author.id)}''')
                fetched = cur.fetchone()
                if not fetched:
                    played, won, lost, bets, winnings, losses, hits, stands, doubledown = 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0
                    cur.execute(f'''INSERT INTO blackjack_stats (discordID, blackjack_played, blackjack_won, blackjack_lost, blackjack_bets, blackjack_winnings, blackjack_losses, blackjack_hits, blackjack_stands, blackjack_doubledown) VALUES ({int(ctx.author.id)}, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0)''')
                    con.commit()
                else:
                    played, won, lost, bets, winnings, losses, hits, stands, doubledown = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8], fetched[9]


                cur.execute(f'''SELECT earned_unpaid, last_paid FROM work WHERE discordID={int(ctx.author.id)}''')
                fetched = cur.fetchone()
                if fetched:
                    earned_unpaid = float(fetched[0])
                    last_paid = int(fetched[1])

                else:
                    cur.execute(f'''INSERT INTO work (discordID, math, geography, sports, culture, grammar, history, biology, chemistry, math_questions, geography_questions, sports_questions, culture_questions, grammar_questions, history_questions, biology_questions, chemistry_questions, education_level, profession, salary, correct_questions, failed_questions, earned_total, worked, paid_taxes, lost_to_irs, last_paid, earned_unpaid) VALUES ({int(ctx.author.id)}, 0,0,0,0,0,0,0,0,"0","0","0","0","0","0","0","0","uneducated", "homeless", 0.0, 0,0, 0.0, 0, 0.0, 0.0, 0, 0)''')
                    con.commit()

                    earned_unpaid = 0
                    last_paid = 0


                moves.append("H")
                hit(player_hand, deck)
                view.remove_item(doubledownbutton)

                if total(player_hand) > 21:
                    newbalance = balance - bet
                    lost += 1
                    losses += bet
                    played += 1
                    bets += bet

                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_lost={lost}, blackjack_bets={bets}, blackjack_losses={losses}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()

                    new_embed = Embed(colour= Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"You have busted, you lose, sorry.", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                elif total(player_hand) == 21:
                    newbalance = balance + bet
                    won += 1
                    winnings += bet
                    played += 1
                    bets += bet
                    earned_unpaid += bet

                    if last_paid == 0:
                        last_paid = round(datetime.datetime.now().timestamp())

                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_won={won}, blackjack_bets={bets}, blackjack_winnings={winnings}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()


                    new_embed = Embed(colour= Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"You got a blackjack! You win!", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                else:
                    new_embed = Embed(colour= Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand[0]), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=view)

            else:
                print("Sum bullshit happened")
                return

        async def stand_callback(interaction):
            if interaction.user == ctx.author:

                cur.execute(f'''SELECT * FROM blackjack_stats WHERE discordID={int(ctx.author.id)}''')
                fetched = cur.fetchone()
                if not fetched:
                    played, won, lost, bets, winnings, losses, hits, stands, doubledown = 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0
                    cur.execute(f'''INSERT INTO blackjack_stats (discordID, blackjack_played, blackjack_won, blackjack_lost, blackjack_bets, blackjack_winnings, blackjack_losses, blackjack_hits, blackjack_stands, blackjack_doubledown) VALUES ({int(ctx.author.id)}, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0)''')
                    con.commit()
                else:
                    played, won, lost, bets, winnings, losses, hits, stands, doubledown = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8], fetched[9]


                cur.execute(f'''SELECT earned_unpaid, last_paid FROM work WHERE discordID={int(ctx.author.id)}''')
                fetched = cur.fetchone()
                if fetched:
                    earned_unpaid = float(fetched[0])
                    last_paid = int(fetched[1])

                else:
                    cur.execute(f'''INSERT INTO work (discordID, math, geography, sports, culture, grammar, history, biology, chemistry, math_questions, geography_questions, sports_questions, culture_questions, grammar_questions, history_questions, biology_questions, chemistry_questions, education_level, profession, salary, correct_questions, failed_questions, earned_total, worked, paid_taxes, lost_to_irs, last_paid, earned_unpaid) VALUES ({int(ctx.author.id)}, 0,0,0,0,0,0,0,0,"0","0","0","0","0","0","0","0","uneducated", "homeless", 0.0, 0,0, 0.0, 0, 0.0, 0.0, 0, 0)''')
                    con.commit()

                    earned_unpaid = 0
                    last_paid = 0


                view.remove_item(doubledownbutton)
                moves.append("S")

                while total(dealer_hand) < 17:
                    hit(dealer_hand, deck)

                if total(player_hand) == 21:
                    newbalance = balance + bet
                    won += 1
                    winnings += bet
                    played += 1
                    bets += bet
                    earned_unpaid += bet

                    if last_paid == 0:
                        last_paid = round(datetime.datetime.now().timestamp())

                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_won={won}, blackjack_bets={bets}, blackjack_winnings={winnings}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()

                    new_embed = discord.Embed(colour= discord.Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"You got a blackjack! You win!", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                if total(dealer_hand) > 21:
                    newbalance = balance + bet
                    won += 1
                    winnings += bet
                    played += 1
                    bets += bet
                    earned_unpaid += bet

                    if last_paid == 0:
                        last_paid = round(datetime.datetime.now().timestamp())

                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_won={won}, blackjack_bets={bets}, blackjack_winnings={winnings}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()

                    new_embed = discord.Embed(colour= discord.Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"Dealer busted! You win!", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                elif total(dealer_hand) == 21:
                    newbalance = balance - bet
                    lost += 1
                    losses += bet
                    played += 1
                    bets += bet

                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_lost={lost}, blackjack_bets={bets}, blackjack_losses={losses}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()

                    new_embed = discord.Embed(colour= discord.Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"Dealer got a blackjack, you lose, sorry.", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                elif total(dealer_hand) >= 17 and total(dealer_hand) < 21 and total(dealer_hand) < total(player_hand):
                    newbalance = balance + bet
                    won += 1
                    winnings += bet
                    played += 1
                    bets += bet
                    earned_unpaid += bet

                    if last_paid == 0:
                        last_paid = round(datetime.datetime.now().timestamp())

                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_won={won}, blackjack_bets={bets}, blackjack_winnings={winnings}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()

                    new_embed = discord.Embed(colour= discord.Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"You have more points than dealer! You win!", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                elif total(dealer_hand) >= 17 and total(dealer_hand) < 21 and total(dealer_hand) > total(player_hand):
                    newbalance = balance - bet
                    lost += 1
                    losses += bet
                    played += 1
                    bets += bet

                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_lost={lost}, blackjack_bets={bets}, blackjack_losses={losses}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()

                    new_embed = discord.Embed(colour= discord.Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"Dealer has more points than you, you lose, sorry.", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                elif total(dealer_hand) >= 17 and total(dealer_hand) < 21 and total(dealer_hand) == total(player_hand):
                    played += 1
                    bets += bet
                    
                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_bets={bets}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()


                    new_embed = discord.Embed(colour= discord.Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"It's a draw! You get your money back.", value=f"Your balance stays the same at: ```py\n${balance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                else:
                    new_embed = discord.Embed(colour= discord.Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=view)

            else:
                print("Sum bullshit happened")
                return

        async def doubledown_callback(interaction):
            if interaction.user == ctx.author:

                cur.execute(f'''SELECT * FROM blackjack_stats WHERE discordID={int(ctx.author.id)}''')
                fetched = cur.fetchone()
                if not fetched:
                    played, won, lost, bets, winnings, losses, hits, stands, doubledown = 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0
                    cur.execute(f'''INSERT INTO blackjack_stats (discordID, blackjack_played, blackjack_won, blackjack_lost, blackjack_bets, blackjack_winnings, blackjack_losses, blackjack_hits, blackjack_stands, blackjack_doubledown) VALUES ({int(ctx.author.id)}, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0)''')
                    con.commit()
                else:
                    played, won, lost, bets, winnings, losses, hits, stands, doubledown = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8], fetched[9]


                cur.execute(f'''SELECT earned_unpaid, last_paid FROM work WHERE discordID={int(ctx.author.id)}''')
                fetched = cur.fetchone()
                if fetched:
                    earned_unpaid = float(fetched[0])
                    last_paid = int(fetched[1])

                else:
                    cur.execute(f'''INSERT INTO work (discordID, math, geography, sports, culture, grammar, history, biology, chemistry, math_questions, geography_questions, sports_questions, culture_questions, grammar_questions, history_questions, biology_questions, chemistry_questions, education_level, profession, salary, correct_questions, failed_questions, earned_total, worked, paid_taxes, lost_to_irs, last_paid, earned_unpaid) VALUES ({int(ctx.author.id)}, 0,0,0,0,0,0,0,0,"0","0","0","0","0","0","0","0","uneducated", "homeless", 0.0, 0,0, 0.0, 0, 0.0, 0.0, 0, 0)''')
                    con.commit()

                    earned_unpaid = 0
                    last_paid = 0


                if balance >= bet*2:
                    hit(player_hand, deck)
                    moves.append("DD")
                
                else:
                    embed = Embed(colour = Colour.purple())
                    embed.add_field(name="Blackjack", value=f"You don't have enough to double down... you lose this hand but not the bet.")
                    embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                if total(player_hand) > 21:
                    newbalance = balance - (bet*2)
                    lost += 1
                    losses += bet
                    played += 1
                    bets += bet*2

                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_lost={lost}, blackjack_bets={bets}, blackjack_losses={losses}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()

                    new_embed = discord.Embed(colour= discord.Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet*2}. *DOUBLED DOWNED*")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"You have busted, you lose, sorry.", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                elif total(player_hand) == 21:
                    newbalance = balance + (bet*2)
                    won += 1
                    winnings += bet
                    played += 1
                    bets += bet*2
                    earned_unpaid += bet*2

                    if last_paid == 0:
                        last_paid = round(datetime.datetime.now().timestamp())

                    for move in moves:
                        if move == "H":hits += 1
                        if move == "S":stands += 1
                        if move == "DD":doubledown += 1


                    cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_won={won}, blackjack_bets={bets}, blackjack_winnings={winnings}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                    cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
                    con.commit()

                    new_embed = discord.Embed(colour= discord.Colour.purple())
                    new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet*2}. *DOUBLED DOWNED*")
                    new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                    new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                    new_embed.add_field(name=f"You got a blackjack! You win!", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                    new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=new_embed, view=None)
                    return

                else:
                    while total(dealer_hand) < 17:
                        hit(dealer_hand, deck)

                    if total(dealer_hand) > 21:
                        newbalance = balance + bet
                        won += 1
                        winnings += bet
                        played += 1
                        bets += bet
                        earned_unpaid += bet

                        if last_paid == 0:
                            last_paid = round(datetime.datetime.now().timestamp())

                        for move in moves:
                            if move == "H":hits += 1
                            if move == "S":stands += 1
                            if move == "DD":doubledown += 1


                        cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                        cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_won={won}, blackjack_bets={bets}, blackjack_winnings={winnings}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                        cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
                        con.commit()

                        new_embed = discord.Embed(colour= discord.Colour.purple())
                        new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                        new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                        new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                        new_embed.add_field(name=f"Dealer busted! You win!", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                        new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                        await interaction.response.edit_message(embed=new_embed, view=None)
                        return

                    elif total(dealer_hand) == 21:
                        newbalance = balance - bet
                        lost += 1
                        losses += bet
                        played += 1
                        bets += bet

                        for move in moves:
                            if move == "H":hits += 1
                            if move == "S":stands += 1
                            if move == "DD":doubledown += 1


                        cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                        cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_lost={lost}, blackjack_bets={bets}, blackjack_losses={losses}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                        con.commit()

                        new_embed = discord.Embed(colour= discord.Colour.purple())
                        new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                        new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                        new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                        new_embed.add_field(name=f"Dealer got a blackjack, you lose, sorry.", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                        new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                        await interaction.response.edit_message(embed=new_embed, view=None)
                        return

                    elif total(dealer_hand) >= 17 and total(dealer_hand) < 21 and total(dealer_hand) < total(player_hand):
                        newbalance = balance + bet
                        won += 1
                        winnings += bet
                        played += 1
                        bets += bet
                        earned_unpaid += bet

                        if last_paid == 0:
                            last_paid = round(datetime.datetime.now().timestamp())

                        for move in moves:
                            if move == "H":hits += 1
                            if move == "S":stands += 1
                            if move == "DD":doubledown += 1


                        cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                        cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_won={won}, blackjack_bets={bets}, blackjack_winnings={winnings}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                        cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
                        con.commit()

                        new_embed = discord.Embed(colour= discord.Colour.purple())
                        new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                        new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                        new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                        new_embed.add_field(name=f"You have more points than dealer! You win!", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                        new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                        await interaction.response.edit_message(embed=new_embed, view=None)
                        return

                    elif total(dealer_hand) >= 17 and total(dealer_hand) < 21 and total(dealer_hand) > total(player_hand):
                        newbalance = balance - bet
                        lost += 1
                        losses += bet
                        played += 1
                        bets += bet

                        for move in moves:
                            if move == "H":hits += 1
                            if move == "S":stands += 1
                            if move == "DD":doubledown += 1


                        cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
                        cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_lost={lost}, blackjack_bets={bets}, blackjack_losses={losses}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
                        con.commit()

                        new_embed = discord.Embed(colour= discord.Colour.purple())
                        new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                        new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                        new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                        new_embed.add_field(name=f"Dealer has more points than you, you lose, sorry.", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
                        new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                        await interaction.response.edit_message(embed=new_embed, view=None)
                        return

                    elif total(dealer_hand) >= 17 and total(dealer_hand) < 21 and total(dealer_hand) == total(player_hand):
                        new_embed = discord.Embed(colour= discord.Colour.purple())
                        new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
                        new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
                        new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"Your moves: {moves}", inline=False)
                        new_embed.add_field(name=f"It's a draw! You get your money back.", value=f"Your balance stays the same at: ```py\n${balance}```", inline=False)
                        new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                        await interaction.response.edit_message(embed=new_embed, view=None)
                        return

            else:
                print("Sum bullshit happened")
                return

        hitbutton.callback = hit_callback
        standbutton.callback = stand_callback
        doubledownbutton.callback = doubledown_callback

        if total(player_hand) == 21:

            cur.execute(f'''SELECT * FROM blackjack_stats WHERE discordID={int(ctx.author.id)}''')
            fetched = cur.fetchone()
            if not fetched:
                played, won, lost, bets, winnings, losses, hits, stands, doubledown = 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0
                cur.execute(f'''INSERT INTO blackjack_stats (discordID, blackjack_played, blackjack_won, blackjack_lost, blackjack_bets, blackjack_winnings, blackjack_losses, blackjack_hits, blackjack_stands, blackjack_doubledown) VALUES ({int(ctx.author.id)}, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0)''')
                con.commit()
            else:
                played, won, lost, bets, winnings, losses, hits, stands, doubledown = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8], fetched[9]

            newbalance = balance + bet
            won += 1
            winnings += bet
            played += 1
            bets += bet

            for move in moves:
                if move == "H":hits += 1
                if move == "S":stands += 1
                if move == "DD":doubledown += 1


            cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
            cur.execute(f'''UPDATE blackjack_stats SET blackjack_played={played}, blackjack_won={won}, blackjack_bets={bets}, blackjack_winnings={winnings}, blackjack_hits={hits}, blackjack_stands={stands}, blackjack_doubledown={doubledown} WHERE discordID={int(ctx.author.id)}''')
            con.commit()

            new_embed = discord.Embed(colour= discord.Colour.purple())
            new_embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
            new_embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand) + " for a total of " + str(total(dealer_hand)), value=f"|", inline=False)
            new_embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"|", inline=False)
            new_embed.add_field(name=f"You got blackjack straight away! Nice!", value=f"Your new balance is: ```py\n${newbalance}```", inline=False)
            new_embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

            await ctx.respond(embed=new_embed)
            return

        embed = discord.Embed(colour= discord.Colour.purple())
        embed.set_author(name=f"Blackjack with @{ctx.author.display_name} for a bet of {bet}")
        embed.add_field(name=f"The dealer is showing a: " + str(dealer_hand[0]), value=f"|", inline=False)
        embed.add_field(name=f"You have a " + str(player_hand) + " for a total of " + str(total(player_hand)), value=f"|", inline=False)
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed = embed, view = view)

 
    @gambling_group.command(name="chances", description="Try a game of chance!") # Chances
    @guild_only()
    async def chances(ctx, bet: Option(float, description="How much to bet?", required=True), chance: Option(int, description="Percentage to win? Higher risk, higher reward and vice versa!", required=True)):
        await ctx.defer()

        passed, balance = await checkbalance(ctx, bet)

        if not passed:
            return
        
        cur.execute(f'''SELECT * FROM chances_stats WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if not fetched:
            played, won, lost, bets, winnings, losses = 0, 0, 0, 0, 0, 0
            cur.execute(f'''INSERT INTO chances_stats (discordID, chances_played, chances_won, chances_lost, chances_bets, chances_winnings, chances_losses) VALUES ({int(ctx.author.id)}, 0, 0, 0, 0.0, 0.0, 0.0)''')
            con.commit()
        
        else:
            played, won, lost, bets, winnings, losses = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6]

        
        if chance <= 0 or chance >= 100:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name="Chances", value=f"Chance can't be nor zero, nor 100! 1-99!")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return
        
        randomint = random.randint(1, 100)
        multiplier = (100 - chance) / 100


        cur.execute(f'''SELECT earned_unpaid, last_paid FROM work WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            earned_unpaid = float(fetched[0])
            last_paid = int(fetched[1])

        else:
            cur.execute(f'''INSERT INTO work (discordID, math, geography, sports, culture, grammar, history, biology, chemistry, math_questions, geography_questions, sports_questions, culture_questions, grammar_questions, history_questions, biology_questions, chemistry_questions, education_level, profession, salary, correct_questions, failed_questions, earned_total, worked, paid_taxes, lost_to_irs, last_paid, earned_unpaid) VALUES ({int(ctx.author.id)}, 0,0,0,0,0,0,0,0,"0","0","0","0","0","0","0","0","uneducated", "homeless", 0.0, 0,0, 0.0, 0, 0.0, 0.0, 0, 0)''')
            con.commit()

            earned_unpaid = 0
            last_paid = 0


        played += 1
        bets += bet*multiplier

        if randomint <= chance:
            newbalance = balance + (bet*multiplier)
            won += 1
            winnings += round(bet*multiplier, 2)
            earned_unpaid += bets

            if last_paid == 0:
                last_paid = round(datetime.datetime.now().timestamp())

            cur.execute(f'''UPDATE chances_stats SET chances_played={played}, chances_won={won}, chances_bets={bets}, chances_winnings={winnings}''')
            cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
            cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
            con.commit()

            embed = Embed(colour = Colour.purple())
            embed.set_author(name="Chances")
            embed.add_field(name="You have won! Congratulations!", value=f"Your new balance is: ```py\n${newbalance}```")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return

        if randomint > chance:
            newbalance = balance - bet
            lost += 1
            losses += bet

            cur.execute(f'''UPDATE chances_stats SET chances_played={played}, chances_lost={lost}, chances_bets={bets}, chances_losses={losses}''')
            cur.execute(f'''UPDATE users SET balance={round(newbalance, 2)} WHERE discordID={int(ctx.author.id)}''')
            con.commit()

            embed = Embed(colour = Colour.purple())
            embed.set_author(name="Chances")
            embed.add_field(name="You lost.. better luck next time!", value=f"Your new balance is: ```py\n${newbalance}```")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return


    @gambling_group.command(name="roulette", description="Roll a marble for some luck.") # Roulette
    @guild_only()
    async def roulette(ctx, bet: Option(float, description="How much to bet?", required=True), slot: Option(str, description="Take a lucky guess...", choices=["Red", "Black", "Odd", "Even", "High (19-36)", "Low (1-18)", "1st 12 (1-12)", "2nd 12 (13-24)", "3rd 12 (25-36)", "0"], required=True)):
        await ctx.defer()

        passed, balance = await checkbalance(ctx, bet)

        if not passed:
            return
        
        cur.execute(f'''SELECT * FROM roulette_stats WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if not fetched:
            played, won, lost, bets, winnings, losses, red, black, odd, even, high, low, st12, nd12, rd12, zero = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            cur.execute(f'''INSERT INTO roulette_stats (discordID, roulette_played, roulette_won, roulette_lost, roulette_bets, roulette_winnings, roulette_losses, roulette_red, roulette_black, roulette_odd, roulette_even, roulette_high, roulette_low, roulette_1st12, roulette_2nd12, roulette_3rd12, roulette_zero) VALUES ({int(ctx.author.id)}, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)''')
            con.commit()
        
        else:
            played, won, lost, bets, winnings, losses, red, black, odd, even, high, low, st12, nd12, rd12, zero = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8], fetched[9], fetched[10], fetched[11], fetched[12], fetched[13], fetched[14], fetched[15], fetched[16]
       

        cur.execute(f'''SELECT earned_unpaid, last_paid FROM work WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            earned_unpaid = float(fetched[0])
            last_paid = int(fetched[1])

        else:
            cur.execute(f'''INSERT INTO work (discordID, math, geography, sports, culture, grammar, history, biology, chemistry, math_questions, geography_questions, sports_questions, culture_questions, grammar_questions, history_questions, biology_questions, chemistry_questions, education_level, profession, salary, correct_questions, failed_questions, earned_total, worked, paid_taxes, lost_to_irs, last_paid, earned_unpaid) VALUES ({int(ctx.author.id)}, 0,0,0,0,0,0,0,0,"0","0","0","0","0","0","0","0","uneducated", "homeless", 0.0, 0,0, 0.0, 0, 0.0, 0.0, 0, 0)''')
            con.commit()

            earned_unpaid = 0
            last_paid = 0


        pocket = random.randint(0, 36)


        roulette_odd = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]
        roulette_even = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
        roulette_red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        roulette_black = [2, 4, 6, 7, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        roulette_high = [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        roulette_low = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        roulette_1st12 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        roulette_2nd12 = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        roulette_3rd12 = [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        roulette_0 = [0]

        landed = []

        if pocket in roulette_odd:landed.append("Odd")
        if pocket in roulette_even:landed.append("Even")
        if pocket in roulette_red:landed.append("Red")
        if pocket in roulette_black:landed.append("Black")
        if pocket in roulette_high:landed.append("High (19-36)")
        if pocket in roulette_low:landed.append("Low (1-18)")
        if pocket in roulette_1st12:landed.append("1st 12 (1-12)")
        if pocket in roulette_2nd12:landed.append("2nd 12 (13-24)")
        if pocket in roulette_3rd12:landed.append("3rd 12 (25-36)")
        if pocket in roulette_0:landed.append("0")


        lowpayout = ["Low (1-18)", "High (19-36)", "Red", "Black", "Even", "Odd"]
        mediumpayout = ["1st 12 (1-12)", "2nd 12 (13-24)", "3rd 12 (25-36)"]
        highpayout = ["0"]


        if slot in lowpayout:newwinbalance = balance + bet
        if slot in mediumpayout:newwinbalance = balance + bet*2
        if slot in highpayout:newwinbalance = balance + bet*35

        newlossbalance = balance - bet

        played += 1
        bets += bet

        newlossbalance = round(newlossbalance, 2)
        newwinbalance = round(newwinbalance, 2)
        bets = round(bets, 2)
       

        match slot:
            case "Odd":
                odd += 1

            case "Even":
                even += 1

            case "Red":
                red += 1

            case "Black":
                black += 1

            case "High (19-36)":
                high += 1

            case "Low (1-18)":
                low += 1

            case "1st 12 (1-12)":
                st12 += 1

            case "2nd 12 (13-24)":
                nd12 += 1

            case "3rd 12 (25-36)":
                rd12 += 1

            case "0":
                zero += 1

        if slot in landed:
            if slot in lowpayout:bet = bet
            if slot in mediumpayout:bet = bet*2
            if slot in highpayout:bet = bet*35

            earned_unpaid += bet

            if last_paid == 0:
                last_paid = round(datetime.datetime.now().timestamp())

            winnings = round(winnings+bet, 2)
            won += 1

            cur.execute(f'''UPDATE users SET balance={newwinbalance} WHERE discordID={int(ctx.author.id)}''')
            cur.execute(f'''UPDATE roulette_stats SET roulette_played={played}, roulette_won={won}, roulette_bets={bets}, roulette_winnings={winnings}, roulette_red={red}, roulette_black={black}, roulette_odd={odd}, roulette_even={even}, roulette_high={high}, roulette_low={low}, roulette_1st12={st12}, roulette_2nd12={nd12}, roulette_3rd12={rd12}, roulette_zero={zero}''')
            cur.execute(f'''UPDATE work SET earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
            con.commit()


            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Roulette [`{pocket}`]", value=f"You got it right! The ball landed on:\n`{landed}`")
            embed.add_field(name="Your new balance is:", value=f"```py\n${newwinbalance}```", inline=False)
            embed.set_image(url="https://www.fruityking.co.uk/wp-content/uploads/2018/07/European-Roulette-min.png")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return
        
        else:
            losses += bet

            losses = round(losses, 2)
            lost += 1

            cur.execute(f'''UPDATE users SET balance={newlossbalance} WHERE discordID={int(ctx.author.id)}''')
            cur.execute(f'''UPDATE roulette_stats SET roulette_played={played}, roulette_lost={lost}, roulette_bets={bets}, roulette_losses={losses}, roulette_red={red}, roulette_black={black}, roulette_odd={odd}, roulette_even={even}, roulette_high={high}, roulette_low={low}, roulette_1st12={st12}, roulette_2nd12={nd12}, roulette_3rd12={rd12}, roulette_zero={zero}''')
            con.commit()


            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Roulette [`{pocket}`]", value=f"Luck wasn't on your side! The ball landed on:\n`{landed}`")
            embed.add_field(name="Your new balance is:", value=f"```py\n${newlossbalance}```", inline=False)
            embed.set_image(url="https://www.fruityking.co.uk/wp-content/uploads/2018/07/European-Roulette-min.png")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return


    @gambling_group.command(name="highlow", description="Will it be higher or lower?") # High Low
    @guild_only()
    async def highlow(ctx, bet: Option(float, description="How much to bet?", required=True)):
        return

    # ========================================= Stats


    @stats_group.command(name="coinflip", description="Get disappointed at your luck.") # Coinflip
    @guild_only()
    async def coinflip(ctx, member: Option(discord.Member, description="Member (Empty if yourself)", default="", required=False)):
        if member == "":
            member = ctx.author
        
        await ctx.defer()

        cur.execute(f'''SELECT * FROM coinflip_stats WHERE discordID={int(member.id)}''')
        fetched = cur.fetchone()

        if not fetched:
            if member == ctx.author:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Coinflip stats for: {member.display_name}", value="You haven't played any coinflip games to have stats, go play some :D")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                return
            if member != ctx.author:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Coinflip stats for: {member.display_name}", value="They haven't played any coinflip games to have stats.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                return
        else:
            played, won, lost, bets, winnings, losses, heads, tails = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8]


        embed = Embed(colour=Colour.purple())
        embed.set_author(name=f"Coinflip stats for: {member.display_name}")
        embed.add_field(name=f"Played: {played}\nWon/Lost", value=f"{won}/{lost}")
        embed.add_field(name=f"Bets made: ${bets}\nWinnings/Losses", value=f"${winnings}/${losses}")
        embed.add_field(name=f"Chose:\nHeads/Tails", value=f"{heads}/{tails}")
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)


    @stats_group.command(name="blackjack", description="Is it 21 though?") # Blackjack
    @guild_only()
    async def blackjack(ctx, member: Option(discord.Member, description="Member (Empty if yourself)", default="", required=False)):
        if member == "":
            member = ctx.author
        
        await ctx.defer()

        cur.execute(f'''SELECT * FROM blackjack_stats WHERE discordID={int(member.id)}''')
        fetched = cur.fetchone()

        if not fetched:
            if member == ctx.author:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Blackjack stats for: {member.display_name}", value="You haven't played any blackjack games to have stats, go play some :D")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                return
            if member != ctx.author:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Blackjack stats for: {member.display_name}", value="They haven't played any blackjack games to have stats.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                return
        else:
            played, won, lost, bets, winnings, losses, hits, stands, doubledowns = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8], fetched[9]


        embed = Embed(colour=Colour.purple())
        embed.set_author(name=f"Blackjack stats for: {member.display_name}")
        embed.add_field(name=f"Played: {played}\nWon/Lost", value=f"{won}/{lost}")
        embed.add_field(name=f"Bets made: ${bets}\nWinnings/Losses", value=f"${winnings}/${losses}")
        embed.add_field(name=f"Moves:\nHeads/Tails/DoubleDowns", value=f"{hits}/{stands}/{doubledowns}")
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)


    @stats_group.command(name="chances", description="What are the chances you're broke?") # Chances
    @guild_only()
    async def chances(ctx, member: Option(discord.Member, description="Member (Empty if yourself)", default="", required=False)):
        if member == "":
            member = ctx.author
        
        await ctx.defer()

        cur.execute(f'''SELECT * FROM chances_stats WHERE discordID={int(member.id)}''')
        fetched = cur.fetchone()

        if not fetched:
            if member == ctx.author:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Chances stats for: {member.display_name}", value="You haven't played any chances games to have stats, go play some :D")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                return
            if member != ctx.author:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Chances stats for: {member.display_name}", value="They haven't played any chances games to have stats.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                return
        else:
            played, won, lost, bets, winnings, losses = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6]


        embed = Embed(colour=Colour.purple())
        embed.set_author(name=f"Chances stats for: {member.display_name}")
        embed.add_field(name=f"Played: {played}\nWon/Lost", value=f"{won}/{lost}")
        embed.add_field(name=f"Bets made: ${bets}\nWinnings/Losses", value=f"${winnings}/${losses}")
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)


    @stats_group.command(name="roulette", description="Roll it!") # Roulette
    @guild_only()
    async def roulette(ctx, member: Option(discord.Member, description="Member (Empty if yourself)", default="", required=False)):
        if member == "":
            member = ctx.author
        
        await ctx.defer()

        cur.execute(f'''SELECT * FROM roulette_stats WHERE discordID={int(member.id)}''')
        fetched = cur.fetchone()

        if not fetched:
            if member == ctx.author:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Roulette stats for: {member.display_name}", value="You haven't played any roulette games to have stats, go play some :D")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                return
            if member != ctx.author:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Roulette stats for: {member.display_name}", value="They haven't played any roulette games to have stats.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                return
        else:
            played, won, lost, bets, winnings, losses, red, black, odd, even, high, low, st12, nd12, rd12, zero = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8], fetched[9], fetched[10], fetched[11], fetched[12], fetched[13], fetched[14], fetched[15], fetched[16]


        embed = Embed(colour=Colour.purple())
        embed.set_author(name=f"Roulette stats for: {member.display_name}")
        embed.add_field(name=f"Played: {played}\nWon/Lost", value=f"{won}/{lost}")
        embed.add_field(name=f"Bets made: ${bets}\nWinnings/Losses", value=f"${winnings}/${losses}")
        embed.add_field(name=f"Bets on:", value=f"Red/Black | Odd/Even | High/Low\n  {red}/{black} | {odd}/{even} | {high}/{low}")
        embed.add_field(name=f"Higher risked bets:", value=f"1st 12/ 2nd 12/ 3rd 12 | Zero\n  {st12}/{nd12}/{rd12} | {zero}")
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)


    # ------------ Count up stats for total TASK
    @tasks.loop(minutes=5)
    async def statroundup(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)

        ttime = datetime.datetime.now()
        time = ttime.strftime("%Y-%m-%d %H:%M:%S - ")
        
        cur.execute('''SELECT discordID FROM users''')
        users = cur.fetchall()
        if users == []:
            print(f"{bcolors.FAIL}{time}[Stat RoundUp] No users in database, returning.{bcolors.ENDC}")
            return
        
        rounded = 0

        for user in users:
            userid = int(user[0])

            cur.execute(f'''SELECT blackjack_played, blackjack_bets, blackjack_winnings, blackjack_losses FROM blackjack_stats WHERE discordID={userid}''')
            blackjackstats = cur.fetchone()
            if not blackjackstats:blackjackstats=[0,0,0,0]

            cur.execute(f'''SELECT chances_played, chances_bets, chances_winnings, chances_losses FROM chances_stats WHERE discordID={userid}''')
            chancesstats = cur.fetchone()
            if not chancesstats:chancesstats=[0,0,0,0]

            cur.execute(f'''SELECT coinflip_played, coinflip_bets, coinflip_winnings, coinflip_losses FROM coinflip_stats WHERE discordID={userid}''')
            coinflipstats = cur.fetchone()
            if not coinflipstats:coinflipstats=[0,0,0,0]

            cur.execute(f'''SELECT roulette_played, roulette_bets, roulette_winnings, roulette_losses FROM roulette_stats WHERE discordID={userid}''')
            roulettestats = cur.fetchone()
            if not roulettestats:roulettestats=[0,0,0,0]

            games_played = blackjackstats[0] + chancesstats[0] + coinflipstats[0] + roulettestats[0]
            amount_bet = blackjackstats[1] + chancesstats[1] + coinflipstats[1] + roulettestats[1]
            winnings = blackjackstats[2] + chancesstats[2] + coinflipstats[2] + roulettestats[2]
            losses = blackjackstats[3] + chancesstats[3] + coinflipstats[3] + roulettestats[3]

            amount_bet = round(amount_bet, 2)
            winnings = round(winnings, 2)
            losses = round(losses, 2)

            cur.execute(f'''UPDATE users SET winnings={winnings}, losses={losses}, games_played={games_played}, amount_bet_in_games={amount_bet} WHERE discordID={userid}''')

            rounded += 1

        con.commit()
        print(f"{bcolors.OKGREEN}{time}[Stat RoundUp] Stats updated for {rounded} user/-s.{bcolors.ENDC}")


def setup(bot):
    bot.add_application_command(gambling_group)
    bot.add_application_command(economics_group)
    bot.add_application_command(stats_group)
    bot.add_cog(Gambling(bot))