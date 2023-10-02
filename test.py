



import sqlite3

con = sqlite3.connect("main.db")
cur = con.cursor()

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
            
        correct_questions INT NOT NULL,
        failed_questions INT NOT NULL,
            
        PRIMARY KEY("discordID")
    )''')