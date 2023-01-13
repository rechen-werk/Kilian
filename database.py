"""
    File name: database.py
    Author:
    This part is responsible for everything related to the database.
"""
import sqlite3
DB = "discord.db"

con = sqlite3.connect(DB)

cur = con.cursor()


try:
    cur.execute("CREATE TABLE student(discord_id, calendar_link, courses, student_id)")
    cur.execute("CREATE TABLE course(lva_nr, semester, lva_type, lva_name, teachers, link)") # teachers?
    cur.execute("CREATE TABLE class(lva_nr, semester, start_time, end_time, location)")

except sqlite3.OperationalError as err:
    print(f"{err.__class__.__name__}: Tables could not be created!")
