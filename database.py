"""
    File name: database.py
    Author:
    This part is responsible for everything related to the database.
"""
import sqlite3

import kusss
from kusss import Student, Course, Class
import sql_queries as query

__DB__ = "discord.db"


class Database:
    def __init__(self):
        self.__con__ = sqlite3.connect(__DB__)
        self.__cur__ = self.__con__.cursor()
        self.__cur__.execute("PRAGMA foreign_keys = ON")
        self.__create_tables__()
        print("Pulling data from KUSSS")
        self.__cur__.executemany(query.insert_course, [c.to_db_entry() for c in kusss.courses()])
        self.__con__.commit()
        print("Update complete")

    def __create_tables__(self):
        self.__cur__.execute(query.create_student)
        self.__cur__.execute(query.create_course)
        self.__cur__.execute(query.create_student_courses)
        self.__cur__.execute(query.create_course_teacher)
        self.__cur__.execute(query.create_class)
        self.__cur__.execute(query.create_roles)

    def insert(self, obj):
        if isinstance(obj, Student):
            self.__cur__.execute(query.insert_student, obj.to_db_entry())
            self.__cur__.executemany(query.insert_student_courses, [(obj.discord_id, course.lva_nr, course.semester) for course in obj.courses])
        elif isinstance(obj, Course):
            self.__cur__.execute(query.insert_course, obj.to_db_entry())
        elif isinstance(obj, Class):
            self.__cur__.execute(query.insert_class, obj.to_db_entry())
        else:
            return NotImplemented
        self.__con__.commit()

    def close(self):
        self.__cur__.close()
        self.__con__.close()


if __name__ == "__main__":
    db = None
    try:
        db = Database()
        c1 = Course("234345", "WS22", "KV", "Course1", [], "c1.live.com")
        c2 = Course("234346", "WS22", "KV", "Course2", [], "c2.evil.com")
        student = Student("lel", "evil.org", {c1, c2}, "k12345678")
        db.insert(student)  # fails because of foreign key constraint
    except sqlite3.OperationalError as err:
        print(f"[{err.sqlite_errorname}]\t{err.args[0]}")
    finally:
        if db:
            db.close()
        print("finished execution")
