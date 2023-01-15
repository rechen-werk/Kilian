"""
    File name: database.py
    Author:
    This part is responsible for everything related to the database.
"""
import sqlite3

from kusss import Student, Course, Class

DB = "discord.db"
con = sqlite3.connect(DB)
cur = con.cursor()

insert_student_query = "INSERT INTO " \
                       "student(discord_id, calendar_link, courses, student_id) " \
                       "VALUES (?,?,?,?)"

insert_course_query = "INSERT INTO " \
                      "course(lva_nr, semester, lva_type, lva_name, teachers, link) " \
                      "VALUES (?,?,?,?)"

insert_class_query = "INSERT INTO " \
                     "class(lva_nr, semester, start_time, end_time, location) " \
                     "VALUES (?,?,?,?)"


def create_tables():
    cur.execute("CREATE TABLE student(discord_id primary key, calendar_link, courses, student_id)")
    cur.execute("CREATE TABLE course(lva_nr primary key, semester, lva_type, lva_name, teachers, link)")  # teachers?
    cur.execute("CREATE TABLE class(lva_nr primary key, semester, start_time, end_time, location)")


def insert(obj):
    if isinstance(obj, Student):
        cur.execute(insert_student_query, obj.to_db_entry())
    elif isinstance(obj, Course):
        cur.execute(insert_course_query, obj.to_db_entry())
    elif isinstance(obj, Class):
        cur.execute(insert_class_query, obj.to_db_entry())
    else:
        return
    con.commit()


try:
    create_tables()
except sqlite3.OperationalError as err:
    print(f"[{err.sqlite_errorname}]\t{err.args[0]}")


student = Student("disc_id", "link.com", set(), "k12345678")
try:
    insert(student)
except sqlite3.IntegrityError as err:
    print(f"[{err.sqlite_errorname}]\t{err.args[0]}")

cur.close()
con.close()
