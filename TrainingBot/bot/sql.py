import sqlite3

con = sqlite3.connect('training_bd.sqlite', check_same_thread=False)
cur = con.cursor()

# cur.executescript('''
# drop table user;
# drop table info_user;
# drop table target_user;
# drop table user_stage_guide;
# ''')

# cur.executescript(
#     '''
#     UPDATE user_stage_guide SET question = 1 WHERE user = 671993577;
#     UPDATE user_stage_guide SET stage = 2 WHERE user = 671993577;
#     '''
# )


# data = [
#     ('В среднем в фруктах содержиться 100 кКл на 100 г', 'Сколько калорий в 300г яблок?', 280, 320),
#     ('', 'Одно среднее яблоко 80 г - сколько примерно калорий в 3 яблоках?', 220, 260),
#     ('В овощах в среднем 20 кКл на 100 г', 'Сколько калорий в салате из овощей массой 300 г?', 40, 80)
# ]


# cur.executemany(
#     '''INSERT INTO guide(advice, question, answer1, answer2) VALUES(?,?,?,?)''',
#     data
# )


# cur.execute(
#     '''drop table guide;'''
# )

cur.executescript('''
DELETE FROM user WHERE id = 907858800;
DELETE FROM info_user WHERE user = 907858800;
DELETE FROM target_user WHERE user = 907858800;
DELETE FROM user_stage_guide WHERE user = 907858800;
''')


# cur.execute(
#     '''
#         CREATE TABLE IF NOT EXISTS quide(
#             advice TEXT DEFAULT "None",
#             question TEXT DEFAULT "None",
#             answer1 INTEGER DEFAULT 0,
#             answer2 INTEGER DEFAULT 0
#         )
#     '''
# )


# cur.execute('''
# CREATE TABLE IF NOT EXISTS user
# (
#     id INTEGER UNIQUE PRIMARY KEY,
#     first_name TEXT,
#     last_name TEXT,
#     username TEXT,
#     password TEXT
# )
# ''')
# con.commit()
# cur.execute('''
# CREATE TABLE IF NOT EXISTS info_user
# (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     height INTEGER,
#     weight INTEGER,
#     gender TEXT,
#     period INTEGER,
#     target INTEGER,
#     user INTEGER NOT NULL UNIQUE,
#     FOREIGN KEY(user) REFERENCES user(id)
# )
# ''')
con.commit()