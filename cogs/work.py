import discord
from discord import guild_only, Embed, Colour
from discord.ext import commands, tasks
from discord.commands import Option
import random
import sqlite3
import asyncio
import datetime

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

# Education = Uneducated, primary-school, high-school, college, bachelor, magister, doctorate, finished
# Work #
# student - uneducated - $2
# Janitor - primary school - $5
# Cashier - high school - $7
# IT Assistant - college - $10
# Accountant - bachelor - $16
# Engineer - magister - $24
# Scientist - doctorate - $30
# CEO - finished - $50

# Income taxes - While in 24h < $100 : Nothing
# In 24h > $100 but < $1000 : If paying - 10% tax, if not 15% deduction from balance after deducting earnings
# In 24h > $1000 : If paying - 12% tax, if not 30% deduction from balance after deducting earnings


# Bank of all money in and out of system

# Member
cur.execute('''
    CREATE TABLE IF NOT EXISTS work (
        discordID INT NOT NULL UNIQUE,

        math INT NOT NULL,
        geography INT NOT NULL,
        sports INT NOT NULL,
        culture INT NOT NULL,
        grammar INT NOT NULL,
        history INT NOT NULL,
        biology INT NOT NULL,
        chemistry INT NOT NULL,
            
        math_questions STR NOT NULL,
        geography_questions STR NOT NULL,
        sports_questions STR NOT NULL,
        culture_questions STR NOT NULL,
        grammar_questions STR NOT NULL,
        history_questions STR NOT NULL,
        biology_questions STR NOT NULL,
        chemistry_questions STR NOT NULL,

            
        education_level STR NOT NULL,

        profession STR NOT NULL,
        
        salary REAL NOT NULL,
        earned_total REAL NOT NULL,
        worked INT NOT NULL,
        paid_taxes REAL NOT NULL,
        lost_to_irs REAL NOT NULL,
            
        earned_unpaid REAL NOT NULL,
            
        correct_questions INT NOT NULL,
        failed_questions INT NOT NULL,
            
        PRIMARY KEY("discordID")
    )''')

# Bank
cur.execute('''
    CREATE TABLE IF NOT EXISTS bank (
        distributed REAL NOT NULL,
        removed REAL NOT NULL,
        
        taxed REAL NOT NULL
    )''')

# Questions
cur.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject STR NOT NULL,
        question STR NOT NULL,
        answer STR NOT NULL
    )''')

subjects = ["math", "geography", "sports", "culture", "grammar", "history", "biology", "chemistry"]

jobs = ["Student", "Janitor", "Cashier", "IT Assistant", "Accountant", "Engineer", "Scientist", "CEO"]


work_group = discord.SlashCommandGroup(name="work", description="Spend your time in the coal mines...")
education_group = discord.SlashCommandGroup(name="education", description="Earn yourself an education!")

dev_group = discord.SlashCommandGroup(name="dev", description="Only developer commands!")
education_dev_group = dev_group.create_subgroup(name="education", description="Only developer commands!")
work_dev_group = dev_group.create_subgroup(name="work", description="Only developer commands!")


async def get_allowed_jobs(ctx: discord.AutocompleteContext):
    cur.execute(f'''SELECT education_level FROM work WHERE discordID={int(ctx.interaction.user.id)}''')
    fetched = cur.fetchone()
    if fetched:
        level = fetched[0]

        match level:
            case "uneducated":
                return ["Student ($2)"]

            case "primary-school":
                return ["Student ($2)", "Janitor ($5)"]

            case "high-school":
                return ["Student ($2)", "Janitor ($5)", "Cashier ($7)"]

            case "college":
                return ["Student ($2)", "Janitor ($5)", "Cashier ($7)", "IT Assistant ($10)"]

            case "bachelor":
                return ["Student ($2)", "Janitor ($5)", "Cashier ($7)", "IT Assistant ($10)", "Accountant ($16)"]

            case "magister":
                return ["Student ($2)", "Janitor ($5)", "Cashier ($7)", "IT Assistant ($10)", "Accountant ($16)", "Engineer ($24)"]

            case "doctorate":
                return ["Student ($2)", "Janitor ($5)", "Cashier ($7)", "IT Assistant ($10)", "Accountant ($16)", "Engineer ($24)", "Scientist ($30)"]

            case "finished":
                return ["Student ($2)", "Janitor ($5)", "Cashier ($7)", "IT Assistant ($10)", "Accountant ($16)", "Engineer ($24)", "Scientist ($30)", "CEO ($50)"]

    else:
        return


class Work(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.checkirs.start()
        

    def cog_unload(self):
        self.checkirs.cancel()

    """
    @education_dev_group.command(name="", description="")
    @guild_only()
    async def cmd(ctx):
        pass
    """

    @education_group.command(name="graduate", description="Graduate to a higher level!") # Graduate
    @guild_only()
    async def graduate(ctx):
        await ctx.defer()

        cur.execute(f'''SELECT education_level, math, geography, sports, culture, grammar, history, biology, chemistry FROM work WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            level = fetched[0]
            math, geography, sports, culture, grammar, history, biology, chemistry = fetched[1], fetched[2], fetched[3], fetched[4], fetched[5], fetched[6], fetched[7], fetched[8]

        else:
            cur.execute(f'''INSERT INTO work (discordID, math, geography, sports, culture, grammar, history, biology, chemistry, math_questions, geography_questions, sports_questions, culture_questions, grammar_questions, history_questions, biology_questions, chemistry_questions, education_level, profession, salary, correct_questions, failed_questions, earned_total, worked, paid_taxes, lost_to_irs, last_paid, earned_unpaid) VALUES ({int(ctx.author.id)}, 0,0,0,0,0,0,0,0,"0","0","0","0","0","0","0","0","uneducated", "homeless", 0.0, 0,0, 0.0, 0, 0.0, 0.0, 0, 0)''')
            con.commit()
            math, geography, sports, culture, grammar, history, biology, chemistry = 0,0,0,0,0,0,0,0
            level = "uneducated"



        needed = []

        if level == "uneducated":
            if math < 3:
                neededmath = 3 - math
                needed.append({"Math":neededmath})

            if grammar < 3:
                neededgrammar = 3 - grammar
                needed.append({"Grammar":neededgrammar})

            if sports < 2:
                neededsports = 2 - sports
                needed.append({"Sports":neededsports})

            if len(needed) == 0:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"Congratulations! You've graduated to **primary-school**!")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                cur.execute(f'''UPDATE work SET education_level="primary-school" WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                await ctx.respond(embed=embed)

                return

            else:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"You could not graduate, you still need {needed} points.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                await ctx.respond(embed=embed)
                return


        if level == "primary-school":
            if math < 10:
                neededmath = 10 - math
                needed.append({"Math":neededmath})

            if grammar < 10:
                neededgrammar = 10 - grammar
                needed.append({"Grammar":neededgrammar})

            if sports < 7:
                neededsports = 7 - sports
                needed.append({"Sports":neededsports})

            if culture < 4:
                neededculture = 7 - culture
                needed.append({"Culture":neededculture})

            if len(needed) == 0:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"Congratulations! You've graduated to **high-school**!")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                cur.execute(f'''UPDATE work SET education_level="high-school" WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                await ctx.respond(embed=embed)

                return

            else:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"You could not graduate, you still need {needed} points.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                await ctx.respond(embed=embed)
                return


        if level == "high-school":
            if math < 25:
                neededmath = 25 - math
                needed.append({"Math":neededmath})

            if grammar < 25:
                neededgrammar = 25 - grammar
                needed.append({"Grammar":neededgrammar})

            if sports < 20:
                neededsports = 20 - sports
                needed.append({"Sports":neededsports})

            if culture < 15:
                neededculture = 15 - culture
                needed.append({"Culture":neededculture})

            if geography < 10:
                neededgeography = 10 - geography
                needed.append({"Geography":neededgeography})

            if history < 10:
                neededhistory = 10 - history
                needed.append({"History":neededhistory})

            if biology < 10:
                neededbiology = 10 - biology
                needed.append({"Biology":neededbiology})

            if chemistry < 10:
                neededchemistry = 10 - chemistry
                needed.append({"Chemistry":neededchemistry})


            if len(needed) == 0:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"Congratulations! You've graduated to **college**!")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                cur.execute(f'''UPDATE work SET education_level="college" WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                await ctx.respond(embed=embed)

                return

            else:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"You could not graduate, you still need {needed} points.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                await ctx.respond(embed=embed)
                return


        if level == "college":
            if math < 40:
                neededmath = 40 - math
                needed.append({"Math":neededmath})

            if grammar < 40:
                neededgrammar = 40 - grammar
                needed.append({"Grammar":neededgrammar})

            if sports < 30:
                neededsports = 30 - sports
                needed.append({"Sports":neededsports})

            if culture < 25:
                neededculture = 25 - culture
                needed.append({"Culture":neededculture})

            if geography < 20:
                neededgeography = 20 - geography
                needed.append({"Geography":neededgeography})

            if history < 25:
                neededhistory = 25 - history
                needed.append({"History":neededhistory})

            if biology < 30:
                neededbiology = 30 - biology
                needed.append({"Biology":neededbiology})

            if chemistry < 30:
                neededchemistry = 30 - chemistry
                needed.append({"Chemistry":neededchemistry})


            if len(needed) == 0:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"Congratulations! You've graduated to **bachelor**!")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                cur.execute(f'''UPDATE work SET education_level="bachelor" WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                await ctx.respond(embed=embed)

                return

            else:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"You could not graduate, you still need {needed} points.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                await ctx.respond(embed=embed)
                return


        if level == "bachelor":
            if math < 60:
                neededmath = 60 - math
                needed.append({"Math":neededmath})

            if grammar < 60:
                neededgrammar = 60 - grammar
                needed.append({"Grammar":neededgrammar})

            if sports < 45:
                neededsports = 45 - sports
                needed.append({"Sports":neededsports})

            if culture < 35:
                neededculture = 35 - culture
                needed.append({"Culture":neededculture})

            if geography < 40:
                neededgeography = 40 - geography
                needed.append({"Geography":neededgeography})

            if history < 40:
                neededhistory = 40 - history
                needed.append({"History":neededhistory})

            if biology < 50:
                neededbiology = 50 - biology
                needed.append({"Biology":neededbiology})

            if chemistry < 50:
                neededchemistry = 50 - chemistry
                needed.append({"Chemistry":neededchemistry})


            if len(needed) == 0:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"Congratulations! You've graduated to **magister**!")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                cur.execute(f'''UPDATE work SET education_level="bachelor" WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                await ctx.respond(embed=embed)

                return

            else:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"You could not graduate, you still need {needed} points.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                await ctx.respond(embed=embed)
                return


        if level == "magister":
            if math < 80:
                neededmath = 80 - math
                needed.append({"Math":neededmath})

            if grammar < 80:
                neededgrammar = 80 - grammar
                needed.append({"Grammar":neededgrammar})

            if sports < 70:
                neededsports = 70 - sports
                needed.append({"Sports":neededsports})

            if culture < 70:
                neededculture = 70 - culture
                needed.append({"Culture":neededculture})

            if geography < 60:
                neededgeography = 60 - geography
                needed.append({"Geography":neededgeography})

            if history < 60:
                neededhistory = 60 - history
                needed.append({"History":neededhistory})

            if biology < 80:
                neededbiology = 80 - biology
                needed.append({"Biology":neededbiology})

            if chemistry < 80:
                neededchemistry = 80 - chemistry
                needed.append({"Chemistry":neededchemistry})


            if len(needed) == 0:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"Congratulations! You've graduated to **doctorate**!")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                cur.execute(f'''UPDATE work SET education_level="doctorate" WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                await ctx.respond(embed=embed)

                return

            else:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"You could not graduate, you still need {needed} points.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                await ctx.respond(embed=embed)
                return


        if level == "doctorate":
            if math < 100:
                neededmath = 100 - math
                needed.append({"Math":neededmath})

            if grammar < 100:
                neededgrammar = 100 - grammar
                needed.append({"Grammar":neededgrammar})

            if sports < 100:
                neededsports = 100 - sports
                needed.append({"Sports":neededsports})

            if culture < 100:
                neededculture = 100 - culture
                needed.append({"Culture":neededculture})

            if geography < 100:
                neededgeography = 100 - geography
                needed.append({"Geography":neededgeography})

            if history < 100:
                neededhistory = 100 - history
                needed.append({"History":neededhistory})

            if biology < 100:
                neededbiology = 100 - biology
                needed.append({"Biology":neededbiology})

            if chemistry < 100:
                neededchemistry = 100 - chemistry
                needed.append({"Chemistry":neededchemistry})


            if len(needed) == 0:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"Congratulations! You've finished school! You won't be able to upgrade your education anymore!")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                cur.execute(f'''UPDATE work SET education_level="finished" WHERE discordID={int(ctx.author.id)}''')
                con.commit()

                await ctx.respond(embed=embed)

                return

            else:
                embed = Embed(colour=Colour.purple())
                embed.add_field(name=f"Graduate", value=f"You could not graduate, you still need {needed} points.")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
                await ctx.respond(embed=embed)
                return


        if level == "finished":
            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Graduate", value=f"You already finished school, no more studying for you!")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")
            await ctx.respond(embed=embed)
            return


    @education_group.command(name="study", description="Study a subject!") # Study
    @guild_only()
    async def study(ctx, subject_chosen: Option(str, choices=subjects, description="Choose a subject, if not it will be random.", default="", required=False)):
        await ctx.defer()

        cur.execute(f'''SELECT * FROM work WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            math_count = int(fetched[1])
            geography_count = int(fetched[2])
            sports_count = int(fetched[3])
            culture_count = int(fetched[4])
            grammar_count = int(fetched[5])
            history_count = int(fetched[6])
            biology_count = int(fetched[7])
            chemistry_count = int(fetched[8])

            math_questions = str(fetched[9])
            geography_questions = str(fetched[10])
            sports_questions = str(fetched[11])
            culture_questions = str(fetched[12])
            grammar_questions = str(fetched[13])
            history_questions = str(fetched[14])
            biology_questions = str(fetched[15])
            chemistry_questions = str(fetched[16])

            correct_questions = int(fetched[20])
            failed_questions = int(fetched[21])

        else:
            cur.execute(f'''INSERT INTO work (discordID, math, geography, sports, culture, grammar, history, biology, chemistry, math_questions, geography_questions, sports_questions, culture_questions, grammar_questions, history_questions, biology_questions, chemistry_questions, education_level, profession, salary, correct_questions, failed_questions, earned_total, worked, paid_taxes, lost_to_irs, last_paid) VALUES ({int(ctx.author.id)}, 0,0,0,0,0,0,0,0,"0","0","0","0","0","0","0","0","uneducated", "homeless", 0.0, 0,0, 0.0, 0, 0.0, 0.0, 0)''')
            con.commit()

            math_count = 0
            geography_count = 0
            sports_count = 0
            culture_count = 0
            grammar_count = 0
            history_count = 0
            biology_count = 0
            chemistry_count = 0

            math_questions = "0"
            geography_questions = "0"
            sports_questions = "0"
            culture_questions = "0"
            grammar_questions = "0"
            history_questions = "0"
            biology_questions = "0"
            chemistry_questions = "0"

            correct_questions = 0
            failed_questions = 0

        dolooping = True

        while dolooping:

    
            if subject_chosen == "":
                subject = random.choice(subjects)
            else:
                subject = subject_chosen
                
        

            id = '0'
            answer = None

        
            if subject == "math":
                if math_count != 130:
                    while id in math_questions:
                        cur.execute(f'''SELECT * FROM questions WHERE subject="{subject}" ORDER BY RANDOM() LIMIT 1''')
                        fetched = cur.fetchone()
                        if fetched:
                            id = f'{fetched[0]}'
                            question = str(fetched[2])
                            answer = str(fetched[3])
                        else:
                            await ctx.respond("Something went wrong1", ephemeral=True)
                            return
                else:
                    await ctx.respond("You've finished math education.", ephemeral=True)

            elif subject == "geography":
                if geography_count != 130:
                    while id in geography_questions:
                        cur.execute(f'''SELECT * FROM questions WHERE subject="{subject}" ORDER BY RANDOM() LIMIT 1''')
                        fetched = cur.fetchone()
                        if fetched:
                            id = str(fetched[0])
                            question = str(fetched[2])
                            answer = str(fetched[3])
                        else:
                            await ctx.respond("Something went wrong1", ephemeral=True)
                            return
                else:
                    await ctx.respond("You've finished geography education.", ephemeral=True)

            elif subject == "sports":
                if sports_count != 130:
                    while id in sports_questions:
                        cur.execute(f'''SELECT * FROM questions WHERE subject="{subject}" ORDER BY RANDOM() LIMIT 1''')
                        fetched = cur.fetchone()
                        if fetched:
                            id = str(fetched[0])
                            question = str(fetched[2])
                            answer = str(fetched[3])
                        else:
                            await ctx.respond("Something went wrong1", ephemeral=True)
                            return
                else:
                    await ctx.respond("You've finished sports education.", ephemeral=True)

            elif subject == "culture":
                if culture_count != 130:
                    while id in culture_questions:
                        cur.execute(f'''SELECT * FROM questions WHERE subject="{subject}" ORDER BY RANDOM() LIMIT 1''')
                        fetched = cur.fetchone()
                        if fetched:
                            id = str(fetched[0])
                            question = str(fetched[2])
                            answer = str(fetched[3])
                        else:
                            await ctx.respond("Something went wrong1", ephemeral=True)
                            return
                else:
                    await ctx.respond("You've finished culture education.", ephemeral=True)

            elif subject == "grammar":
                if grammar_count != 130:
                    while id in grammar_questions:
                        cur.execute(f'''SELECT * FROM questions WHERE subject="{subject}" ORDER BY RANDOM() LIMIT 1''')
                        fetched = cur.fetchone()
                        if fetched:
                            id = str(fetched[0])
                            question = str(fetched[2])
                            answer = str(fetched[3])
                        else:
                            await ctx.respond("Something went wrong1", ephemeral=True)
                            return
                else:
                    await ctx.respond("You've finished grammar education.", ephemeral=True)

            elif subject == "history":
                if history_count != 100:
                    while id in history_questions:
                        cur.execute(f'''SELECT * FROM questions WHERE subject="{subject}" ORDER BY RANDOM() LIMIT 1''')
                        fetched = cur.fetchone()
                        if fetched:
                            id = str(fetched[0])
                            question = str(fetched[2])
                            answer = str(fetched[3])
                        else:
                            await ctx.respond("Something went wrong1", ephemeral=True)
                            return
                else:
                    await ctx.respond("You've finished history education.", ephemeral=True)

            elif subject == "biology":
                if biology_count != 130:
                    while id in biology_questions:
                        cur.execute(f'''SELECT * FROM questions WHERE subject="{subject}" ORDER BY RANDOM() LIMIT 1''')
                        fetched = cur.fetchone()
                        if fetched:
                            id = str(fetched[0])
                            question = str(fetched[2])
                            answer = str(fetched[3])
                        else:
                            await ctx.respond("Something went wrong1", ephemeral=True)
                            return
                else:
                    await ctx.respond("You've finished biology education.", ephemeral=True)

            elif subject == "chemistry":
                if chemistry_count != 130:
                    while id in chemistry_questions:
                        cur.execute(f'''SELECT * FROM questions WHERE subject="{subject}" ORDER BY RANDOM() LIMIT 1''')
                        fetched = cur.fetchone()
                        if fetched:
                            id = str(fetched[0])
                            question = str(fetched[2])
                            answer = str(fetched[3])
                        else:
                            await ctx.respond("Something went wrong1", ephemeral=True)
                            return
                else:
                    await ctx.respond("You've finished chemistry education.", ephemeral=True)

            else:
                await ctx.respond("Something went wrong", ephemeral=True)
                return


            wrong = []


            while len(wrong) < 3:
                cur.execute(f'''SELECT answer FROM questions WHERE subject="{subject}" ORDER BY RANDOM() LIMIT 1''')
                fetched = cur.fetchone()
                if fetched:
                        if str(fetched[0]) != answer and answer != None and str(fetched[0]) not in wrong: 
                            wrong.append(str(fetched[0]))

                        elif str(fetched[0]) == answer or str(fetched[0]) in wrong:
                            #print("New wrong is same as answer or another wrong")
                            continue

                        else:
                            print("AHHHHHHHHHHHHHHHHHHHHHHH")
                            print(f"answer: {answer}")
                            print(f"wrongs: {wrong}")
                            await asyncio.sleep(1)
                            continue
                else:
                    continue

                        
            answer_label = random.randint(1,4)
            
            # 1️⃣ 2️⃣ 3️⃣ 4️⃣

            buttonone = discord.ui.Button(label=f"{answer if answer_label == 1 else wrong.pop()}", style=discord.ButtonStyle.secondary)
            buttontwo = discord.ui.Button(label=f"{answer if answer_label == 2 else wrong.pop()}", style=discord.ButtonStyle.secondary)
            buttonthree = discord.ui.Button(label=f"{answer if answer_label == 3 else wrong.pop()}", style=discord.ButtonStyle.secondary)
            buttonfour = discord.ui.Button(label=f"{answer if answer_label == 4 else wrong.pop()}", style=discord.ButtonStyle.secondary)


            view = discord.ui.View(timeout=30)
            view.add_item(buttonone)
            view.add_item(buttontwo)
            view.add_item(buttonthree)
            view.add_item(buttonfour)


            async def on_timeout():
                view.disable_all_items()

                nonlocal failed_questions
                failed_questions += 1

                cur.execute(f'''UPDATE work SET failed_questions={failed_questions} WHERE discordID={ctx.author.id}''')
                con.commit()


            async def rightcallback(interaction):
                if ctx.author == interaction.user:   
                    nonlocal math_count, geography_count, sports_count, culture_count, grammar_count, history_count, biology_count, chemistry_count, correct_questions, failed_questions, math_questions, geography_questions, sports_questions, culture_questions, grammar_questions, history_questions, biology_questions, chemistry_questions
                    match subject:
                        case "math":
                            math_count += 1
                            math_questions = f"{math_questions},{id}"
                            correct_questions += 1
                        
                        case "geography":
                            geography_count += 1
                            geography_questions = f"{geography_questions},{id}"
                            correct_questions += 1

                        case "sports":
                            sports_count += 1
                            sports_questions = f"{sports_questions},{id}"
                            correct_questions += 1

                        case "culture":
                            culture_count += 1
                            culture_questions = f"{culture_questions},{id}"
                            correct_questions += 1

                        case "grammar":
                            grammar_count += 1
                            grammar_questions = f"{grammar_questions},{id}"
                            correct_questions += 1

                        case "history":
                            history_count += 1
                            history_questions = f"{history_questions},{id}"
                            correct_questions += 1

                        case "biology":
                            biology_count += 1
                            biology_questions = f"{biology_questions},{id}"
                            correct_questions += 1

                        case "chemistry":
                            chemistry_count += 1
                            chemistry_questions = f"{chemistry_questions},{id}"
                            correct_questions += 1


                    cur.execute(f'''UPDATE work SET math={math_count}, geography={geography_count}, sports={sports_count}, culture={culture_count}, grammar={grammar_count}, history={history_count}, biology={biology_count}, chemistry={chemistry_count}, math_questions="{math_questions}", geography_questions="{geography_questions}", sports_questions="{sports_questions}", culture_questions="{culture_questions}", grammar_questions="{grammar_questions}", history_questions="{history_questions}", biology_questions="{biology_questions}", chemistry_questions="{chemistry_questions}", correct_questions={correct_questions}, failed_questions={failed_questions} WHERE discordID={ctx.author.id}''')
                    con.commit()


                    embed = Embed(colour=Colour.purple())
                    embed.add_field(name=f"Study `{subject}`", value=f"***You got it right!***")
                    embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=embed, view=None)
                else:
                    await interaction.user.send("Don't answer questions that are not yours!")


            async def wrongcallback(interaction):
                if ctx.author == interaction.user:
                    nonlocal failed_questions
                    failed_questions += 1

                    cur.execute(f'''UPDATE work SET failed_questions={failed_questions} WHERE discordID={ctx.author.id}''')
                    con.commit()

                    embed = Embed(colour=Colour.purple())
                    embed.add_field(name=f"Study `{subject}`", value=f"***You got it wrong!***")
                    embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                    await interaction.response.edit_message(embed=embed, view=None)
                else:
                    await interaction.user.send("Don't answer questions that are not yours!")


            if answer_label == 1:
                buttonone.callback = rightcallback
                buttontwo.callback = wrongcallback
                buttonthree.callback = wrongcallback
                buttonfour.callback = wrongcallback

            if answer_label == 2:
                buttonone.callback = wrongcallback
                buttontwo.callback = rightcallback
                buttonthree.callback = wrongcallback
                buttonfour.callback = wrongcallback

            if answer_label == 3:
                buttonone.callback = wrongcallback
                buttontwo.callback = wrongcallback
                buttonthree.callback = rightcallback
                buttonfour.callback = wrongcallback

            if answer_label == 4:
                buttonone.callback = wrongcallback
                buttontwo.callback = wrongcallback
                buttonthree.callback = wrongcallback
                buttonfour.callback = rightcallback

            view.on_timeout = on_timeout

            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Study `{subject}` | Timeout = 30sec", value=f"***{question}***")
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")


            await ctx.respond(embed=embed, view=view)
            dolooping = False


    @education_group.command(name="statistics", description="Look at your statistics!") # Statistics
    @guild_only()
    async def statistics(ctx, member: Option(discord.Member, description="Member who's diploma to look at", required=False, default="")):
        await ctx.defer()

        if member == "":
            cur.execute(f'''SELECT * FROM work WHERE discordID={int(ctx.author.id)}''')
            fetched = cur.fetchone()
            if fetched:
                math_count = int(fetched[1])
                geography_count = int(fetched[2])
                sports_count = int(fetched[3])
                culture_count = int(fetched[4])
                grammar_count = int(fetched[5])
                history_count = int(fetched[6])
                biology_count = int(fetched[7])
                chemistry_count = int(fetched[8])

                education_level = str(fetched[17])

                correct_questions = int(fetched[20])
                failed_questions = int(fetched[21])

            else:
                embed = Embed(colour=Colour.purple())
                embed.set_author(name=f"Study statistics - [{ctx.author.display_name}]")
                embed.add_field(name=f"You don't have any statistics!", value=f"Go answer some questions with /work education study")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                await ctx.respond(embed=embed)
                return
            
            embed = Embed(colour=Colour.purple())
            embed.set_author(name=f"Study statistics - [{ctx.author.display_name}]")
            embed.add_field(name=f"Math questions:", value=f"`{math_count}/130`", inline=False)
            embed.add_field(name=f"Geography questions:", value=f"`{geography_count}/130`", inline=False)
            embed.add_field(name=f"Sports questions:", value=f"`{sports_count}/130`", inline=False)
            embed.add_field(name=f"Culture questions:", value=f"`{culture_count}/130`", inline=False)
            embed.add_field(name=f"Grammar questions:", value=f"`{grammar_count}/130`", inline=False)
            embed.add_field(name=f"History questions:", value=f"`{history_count}/100`", inline=False)
            embed.add_field(name=f"Biology questions:", value=f"`{biology_count}/130`", inline=False)
            embed.add_field(name=f"Chemistry questions:", value=f"`{chemistry_count}/130`", inline=False)
            embed.add_field(name=f"Education level:", value=f"`{education_level}`", inline=True)
            embed.add_field(name=f"Correct questions:", value=f"`{correct_questions}`", inline=True)
            embed.add_field(name=f"Failed questions:", value=f"`{failed_questions}`", inline=True)
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

            await ctx.respond(embed=embed)

        if member != "":
            cur.execute(f'''SELECT * FROM work WHERE discordID={int(member.id)}''')
            fetched = cur.fetchone()
            if fetched:
                math_count = int(fetched[1])
                geography_count = int(fetched[2])
                sports_count = int(fetched[3])
                culture_count = int(fetched[4])
                grammar_count = int(fetched[5])
                history_count = int(fetched[6])
                biology_count = int(fetched[7])
                chemistry_count = int(fetched[8])

                education_level = str(fetched[17])

                correct_questions = int(fetched[20])
                failed_questions = int(fetched[21])

            else:
                embed = Embed(colour=Colour.purple())
                embed.set_author(name=f"Study statistics - [{member.display_name}]")
                embed.add_field(name=f"They don't have any statistics!", value=f"Make them answer some questions with /work education study")
                embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

                await ctx.respond(embed=embed)
                return
            
            embed = Embed(colour=Colour.purple())
            embed.set_author(name=f"Study statistics - [{member.display_name}]")
            embed.add_field(name=f"Math questions:", value=f"`{math_count}/130`", inline=False)
            embed.add_field(name=f"Geography questions:", value=f"`{geography_count}/130`", inline=False)
            embed.add_field(name=f"Sports questions:", value=f"`{sports_count}/130`", inline=False)
            embed.add_field(name=f"Culture questions:", value=f"`{culture_count}/130`", inline=False)
            embed.add_field(name=f"Grammar questions:", value=f"`{grammar_count}/130`", inline=False)
            embed.add_field(name=f"History questions:", value=f"`{history_count}/100`", inline=False)
            embed.add_field(name=f"Biology questions:", value=f"`{biology_count}/130`", inline=False)
            embed.add_field(name=f"Chemistry questions:", value=f"`{chemistry_count}/130`", inline=False)
            embed.add_field(name=f"Education level:", value=f"`{education_level}`", inline=True)
            embed.add_field(name=f"Correct questions:", value=f"`{correct_questions}`", inline=True)
            embed.add_field(name=f"Failed questions:", value=f"`{failed_questions}`", inline=True)
            embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

            await ctx.respond(embed=embed)


    @work_group.command(name="help", description="Help about all this bs") # Help
    @guild_only()
    async def help(ctx):
        await ctx.defer()

        embed = Embed(colour=Colour.purple())
        embed.set_author(name=f"Work help")
        embed.add_field(name=f"/work education study `subject`", value=f"Used to level up your 'education' at specific (or random) subjects using trivia questions. If you want to see how many levels at each subject you need for a graduation, use /work education graduate", inline=False) # Education Study
        embed.add_field(name=f"/work education graduate", value=f"Used to level up your education. The higher the level, the better paying jobs you can get.", inline=False) # Education Graduate
        embed.add_field(name=f"/work education statistics `member`", value=f"Check on your or another members' education statistics. Compete for the most correct and least failed questions?", inline=False) # Education Statistics
        embed.add_field(name=f"***This*** -> /work help", value=f"A help command... literally this.", inline=False) # Work Help
        embed.add_field(name=f"/work job `job`", value=f"Used to select a job. Your options are available and shown only when you unlock them, so don't worry that you can't see all of them.", inline=False) # Work Job
        embed.add_field(name=f"/work challenge `amount`", value=f"Challenge your 'boss' to give you a raise. Has a cooldown of 10 minutes(per member).", inline=False) # Work Challenge
        embed.add_field(name=f"/work work", value=f"Go to work, earn your salary. Has a cooldown of 1 minute(per member).", inline=False) # Work Work
        embed.add_field(name=f"/work taxes `action`", value=f"With `check` option you can see how much you need to pay in taxes(if at all), and till when you need to. With `pay` option you will automatically pay them.", inline=False) # Work Taxes
        embed.add_field(name=f"/work statistics `member`", value=f"Check on your or another members' work ethic. See who has a higher paying job? (WIP)", inline=False) # Work Statistics
        embed.add_field(name=f"Taxes and IRS!", value=f"So, you earn money and think none of them have to go to taxes? Nah boi, this is capitalism. When you earn money, if it's your first time since paying or first time in general, your time will be logged and you'll have 24h to pay. If you earn less than `$100`, no need to pay. If you earn > `$100`, but < `$1000`, you need to either pay 10% of your earnings, or all of them get taken away and an additional 15% from your balance gets taken as fees. If you earn > `$1000`, you need to pay 12% income tax or all of that gets taken away and 30% deduction from your balance as fees. Remember to pay your taxes.", inline=False) # Work IRS 
        embed.set_footer(text=f"Dreampack - executed by @{ctx.author.display_name}")

        await ctx.respond(embed=embed)
    

    @work_group.command(name="job", description="Get or change your job!") # Job
    @guild_only()
    async def job(ctx, job: Option(str, description="What job do you want?", autocomplete=discord.utils.basic_autocomplete(get_allowed_jobs), required=True)):
        await ctx.defer()

        match job:
            case "Student ($2)":
                cur.execute(f'''UPDATE work SET profession="Student", salary=2.0 WHERE discordID={int(ctx.author.id)}''')
                con.commit()

            case "Janitor ($5)":
                cur.execute(f'''UPDATE work SET profession="Janitor", salary=5.0 WHERE discordID={int(ctx.author.id)}''')
                con.commit()

            case "Cashier ($7)":
                cur.execute(f'''UPDATE work SET profession="Cashier", salary=7.0 WHERE discordID={int(ctx.author.id)}''')
                con.commit()

            case "IT Assistant ($10)":
                cur.execute(f'''UPDATE work SET profession="IT Assistant", salary=10.0 WHERE discordID={int(ctx.author.id)}''')
                con.commit()

            case "Accountant ($16)":
                cur.execute(f'''UPDATE work SET profession="Accountant", salary=16.0 WHERE discordID={int(ctx.author.id)}''')
                con.commit()

            case "Engineer ($24)":
                cur.execute(f'''UPDATE work SET profession="Engineer", salary=24.0 WHERE discordID={int(ctx.author.id)}''')
                con.commit()

            case "Scientist ($30)":
                cur.execute(f'''UPDATE work SET profession="Scientist", salary=30.0 WHERE discordID={int(ctx.author.id)}''')
                con.commit()

            case "CEO ($50)":
                cur.execute(f'''UPDATE work SET profession="CEO", salary=50.0 WHERE discordID={int(ctx.author.id)}''')
                con.commit()
        
        embed = Embed(colour=Colour.purple())
        embed.add_field(name=f"Job Listing", value=f"You have gotten a {job} profession!")
        embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

        await ctx.respond(embed=embed)
    

    @work_group.command(name="challenge", description="Challenge your boss to give you a raise!") # Challenge
    @guild_only()
    @commands.cooldown(1, 600, type=commands.BucketType.member)
    async def challenge(ctx, percentage: Option(str, description="How big of a raise? (example: 4%)", required=True)):
        percentage = percentage.replace("%", "")
        percentage = percentage.strip()
        percentage = round(float(percentage), 2)

        if percentage > 10:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Boss Challenge", value=f"Can't ask for a raise higher than 10%")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return

        cur.execute(f'''SELECT salary FROM work WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            salary = round(float(fetched[0]))
        else:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Boss Challenge", value=f"You don't seem to have a job at all... go get one with /work job")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return
        

        increase = (salary*percentage)/100

        randomint = random.randint(1, 100)

        if randomint <= 30:
            # Win
            newsalary = salary + increase

            cur.execute(f'''UPDATE work SET salary={round(newsalary, 2)} WHERE discordID={int(ctx.author.id)}''')
            con.commit()

            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Boss Challenge", value=f"You got the raise! Your new salary: ```py\n${newsalary}```")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return

        else:
            # No
            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Boss Challenge", value=f"You did not get the raise...")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return


    @work_group.command(name="work", description="I have to go to work...") # Work
    @guild_only()
    @commands.cooldown(1, 60, type=commands.BucketType.member)
    async def work(ctx):
        cur.execute(f'''SELECT salary, earned_total, worked, earned_unpaid, last_paid FROM work WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            salary = round(float(fetched[0]))
            earned_total = round(float(fetched[1]))
            worked = int(fetched[2])
            earned_unpaid = round(float(fetched[3]), 2)
            last_paid = int(fetched[4])

        else:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Work", value=f"You don't seem to have a job at all... go get one with /work job")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return
        

        cur.execute(f'''SELECT balance FROM users WHERE discordID={int(ctx.author.id)}''')
        fetched = cur.fetchone()
        if fetched:
            balance = round(float(fetched[0]))
        else:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Work", value=f"You don't seem to have a bank account.. Check you balance with /econ balance for a starting $100!")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return

        
        cur.execute(f'''SELECT distributed FROM bank''')
        fetched = cur.fetchone()
        if fetched:
            distributed = round(float(fetched[0]))
        else:
            cur.execute(f'''INSERT INTO bank (distributed, removed, taxed) VALUES (0.0, 0.0, 0.0)''')
            con.commit()
            distributed = 0.0


        newbalance = round(balance + salary, 2)
        earned_total += salary
        worked += 1
        distributed += salary
        earned_unpaid += salary

        if last_paid == 0:
            last_paid = round(datetime.datetime.now().timestamp())


        cur.execute(f'''UPDATE users SET balance={newbalance} WHERE discordID={int(ctx.author.id)}''')
        cur.execute(f'''UPDATE work SET earned_total={round(earned_total, 2)}, worked={worked}, earned_unpaid={round(earned_unpaid, 2)}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
        cur.execute(f'''UPDATE bank SET distributed={round(distributed, 2)}''')
        con.commit()


        embed = Embed(colour=Colour.purple())
        embed.add_field(name=f"Work", value=f"You did some fine work. Your new balance: ```py\n${newbalance}```")
        embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

        await ctx.respond(embed=embed)


    @work_group.command(name="taxes", description="Talk to IRS.") # Taxes
    @guild_only()
    async def taxes(ctx, action: Option(str, choices=["pay", "check"], required=True)):
        
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

        if earned_unpaid < 100:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Taxes", value=f"Your income is so small, you aren't being taxed.")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")
            await ctx.respond(embed=embed)
            return

        if earned_unpaid >= 100:
            cur.execute(f'''SELECT balance FROM users WHERE discordID={int(ctx.author.id)}''')
            fetched = cur.fetchone()
            if fetched:
                balance = float(fetched[0])

        if balance <= 1:
            embed = Embed(colour=Colour.purple())
            embed.add_field(name=f"Taxes", value=f"Your balance is so low you aren't gettin taxed right now.")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")
            await ctx.respond(embed=embed)
            return

        cur.execute(f'''SELECT taxed FROM bank''')
        fetched = cur.fetchone()
        if fetched:
            taxed = float(fetched[0])
            
        
        if earned_unpaid >= 100 and earned_unpaid <= 1000: # Taxes apply below $1000, that is 10% tax, if not 15% deduction from balance after deducting earnings
            taxpercentage = 10
            taxamount = round(earned_unpaid * 0.10, 2)

            balancepercentage = 15
            balanceamount = round(balance * 0.15, 2)
            

        if earned_unpaid > 1000: # Taxes apply above $1000, 12% tax, if not 30% deduction from balance after deducting earnings
            taxpercentage = 12
            taxamount = round(earned_unpaid * 0.12, 2)

            balancepercentage = 30
            balanceamount = round(balance * 0.30, 2)

            
        paytill = last_paid + 86400

        if action == "check":
            embed = Embed(colour=Colour.purple())
            embed.set_author(name="Taxes")
            embed.add_field(name=f"Unpaid earnings: {earned_unpaid}", value=f"That means you need to pay {taxpercentage}% which is {taxamount} till <t:{paytill}:R>. If you don't, the IRS will take your whole earnings and also deduct {balancepercentage}% from your balance which would amount to {balanceamount}")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

            await ctx.respond(embed=embed)
            return

        if action == "pay":
            earned_unpaid = 0
            last_paid = 0
            newbalance = round(balance - taxamount, 2)
            taxed = round(taxed+taxamount, 2)

            cur.execute(f'''UPDATE work SET earned_unpaid={earned_unpaid}, last_paid={last_paid} WHERE discordID={int(ctx.author.id)}''')
            cur.execute(f'''UPDATE users SET balance={newbalance} WHERE discordID={int(ctx.author.id)}''')
            cur.execute(f'''UPDATE bank SET taxed={taxed}''')
            con.commit()
            
            embed = Embed(colour=Colour.purple())
            embed.set_author(name="Taxes")
            embed.add_field(name=f"Unpaid earnings: {earned_unpaid}", value=f"You paid {taxpercentage}% which is {taxamount}.")
            embed.set_footer(text=f"Dreampack - executed by {ctx.author.display_name}")

            await ctx.respond(embed=embed)


    @work_group.command(name="statistics", description="Look at your work statistics!") # Statistics
    @guild_only()
    async def statistics(ctx, member: Option(discord.Member, description="Member who's contract to look at", required=False, default="")):
        return


    @tasks.loop(minutes=2)
    async def checkirs(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)
        guild = self.bot.get_guild(773626027347017748)

        timestamp = round(datetime.datetime.now().timestamp())

        cur.execute(f'''SELECT removed FROM bank''')
        removed = cur.fetchone()[0]

        cur.execute(f'''SELECT discordID, earned_unpaid, last_paid FROM work''')
        fetched = cur.fetchall()

        robbed_people = 0

        for member in fetched:
            if float(member[1]) > 100 and float(member[1] < 1000): # Taxes apply below $1000, that is 10% tax, if not 15% deduction from balance after deducting earnings
                if int(member[2]) <= timestamp - 86400: # 24H have passed
                    cur.execute(f'''SELECT balance FROM users WHERE discordID={int(member[0])}''')
                    user = cur.fetchone()
                    balance = round(float(user[0]), 2)

                    if balance <= 1:
                        continue

                    newbalance = round((balance-member[1])-(balance*0.15), 2) # (balance - earned) - (15% of balance)
                    removed += round(float(member[1])+(balance*0.15), 2)
                    robbed_people += 1

                    cur.execute(f'''UPDATE users SET balance={newbalance} WHERE discordID={int(member[0])}''')
                    cur.execute(f'''UPDATE work SET earned_unpaid=0.0, last_paid=0 WHERE discordID={int(member[0])}''')

                    member_name = await guild.fetch_member(int(member[0]))

                    ttime = datetime.datetime.now()
                    time = ttime.strftime("%Y-%m-%d %H:%M:%S - ")
                    
                    print(f"{bcolors.OKCYAN}{time}[IRS] {member_name.display_name} has been tax robbed for: {round(float(member[1])+(balance*0.15), 2)}!{bcolors.ENDC}")
                else:
                    continue
            
            if float(member[1]) > 1000: # Taxes apply above $1000, 12% tax, if not 30% deduction from balance after deducting earnings
                if int(member[2]) <= timestamp - 86400: # 24H have passed
                    cur.execute(f'''SELECT balance FROM users WHERE discordID={int(member[0])}''')
                    user = cur.fetchone()
                    balance = round(float(user[0]), 2)

                    if balance <= 1:
                        continue

                    newbalance = round((balance-float(member[1]))-(balance*0.30), 2)
                    removed += round(float(member[1])+(balance*0.30), 2)
                    robbed_people += 1

                    cur.execute(f'''UPDATE users SET balance={newbalance} WHERE discordID={int(member[0])}''')
                    cur.execute(f'''UPDATE work SET earned_unpaid=0.0, last_paid=0 WHERE discordID={int(member[0])}''')

                    member_name = await guild.fetch_member(int(member[0]))

                    ttime = datetime.datetime.now()
                    time = ttime.strftime("%Y-%m-%d %H:%M:%S - ")
                    
                    print(f"{bcolors.OKCYAN}{time}[IRS] {member_name.display_name} has been tax robbed for: {round(float(member[1])+(balance*0.30), 2)}!{bcolors.ENDC}")
                else:
                    continue

            if float(member[1]) < 100 and int(member[2]) <= timestamp - 86400 and float(member[1]) > 0:
                cur.execute(f'''UPDATE work SET earned_unpaid=0.0, last_paid=0 WHERE discordID={int(member[0])}''')

                member_name = await guild.fetch_member(int(member[0]))

                ttime = datetime.datetime.now()
                time = ttime.strftime("%Y-%m-%d %H:%M:%S - ")
                
                print(f"{bcolors.OKCYAN}{time}[IRS] {member_name.display_name} has been cleared of income.{bcolors.ENDC}")
        
        ttime = datetime.datetime.now()
        time = ttime.strftime("%Y-%m-%d %H:%M:%S - ")

        con.commit()
        if robbed_people > 0:
            print(f"{bcolors.OKCYAN}{time}[IRS] {robbed_people} have been tax robbed!{bcolors.ENDC}")





def setup(bot):
    bot.add_application_command(work_group)
    bot.add_application_command(dev_group)
    bot.add_cog(Work(bot))