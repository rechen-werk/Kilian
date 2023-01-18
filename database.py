"""
    File name: database.py
    Author:
    This part is responsible for everything related to the database.
"""
import sqlite3

import kusss
from kusss import Student, Course, Class

__DB__ = "discord.db"

__insert_student_query__ = "REPLACE INTO " \
                           "student(discord_id, student_id, calendar_link) " \
                           "VALUES (?,?,?)"

__insert_course_query__ = "REPLACE INTO " \
                          "course(lva_nr, semester, lva_type, lva_name, link) " \
                          "VALUES (?,?,?,?,?)"

__insert_student_courses_query__ = "REPLACE INTO " \
                          "student_courses(discord_id, lva_nr, semester) " \
                          "VALUES (?,?,?)"

__insert_class_query__ = "REPLACE INTO " \
                         "class(lva_nr, semester, start_time, end_time, location) " \
                         "VALUES (?,?,?,?)"


class Database:
    def __init__(self):
        self.__con__ = sqlite3.connect(__DB__)
        self.__cur__ = self.__con__.cursor()
        self.__create_tables__()
        print("Pulling data from KUSSS")
        self.__cur__.executemany(__insert_course_query__, [c.to_db_entry() for c in kusss.courses()])
        print("Update complete")

    def __create_tables__(self):
        self.__cur__.execute(
            "CREATE TABLE IF NOT EXISTS student("
            "discord_id text not null, "  # integer?
            "student_id text nullable, "
            "calendar_link text not null,"
            "primary key (discord_id)"
            ")"
        )
        self.__cur__.execute(
            "CREATE TABLE IF NOT EXISTS course("
            "lva_nr text not null, "
            "semester text not null, "
            "lva_type text not null , "
            "lva_name text not null , "
            "link text not null, "
            "primary key (lva_nr, semester)"
            ")"
        )
        self.__cur__.execute(
            "CREATE TABLE IF NOT EXISTS student_courses("
            "discord_id text not null, "
            "semester text not null, "
            "lva_nr text not null, "
            "foreign key (discord_id) references student(discord_id),"
            "foreign key (semester, lva_nr) references course(semester, lva_nr)"
            ")"
        )
        self.__cur__.execute(
            "CREATE TABLE IF NOT EXISTS course_teachers("
            "teacher_name text unique not null, "  # maybe not unique?
            "semester text not null,"
            "lva_nr integer not null, "
            "primary key (teacher_name, semester, lva_nr)"
            ")"
        )
        self.__cur__.execute(
            "CREATE TABLE IF NOT EXISTS class("
            "lva_nr text not null, "
            "semester text not null, "
            "start_time integer not null, "
            "end_time integer not null, "
            "location text not null,"
            "primary key (lva_nr, semester, start_time, end_time, location)"
            ")"
        )

    def insert(self, obj):
        if isinstance(obj, Student):
            self.__cur__.execute(__insert_student_query__, obj.to_db_entry())
            self.__cur__.executemany(__insert_student_courses_query__, [(obj.discord_id, course.lva_nr, course.semester) for course in obj.courses])
        elif isinstance(obj, Course):
            self.__cur__.execute(__insert_course_query__, obj.to_db_entry())
        elif isinstance(obj, Class):
            self.__cur__.execute(__insert_class_query__, obj.to_db_entry())
        else:
            return NotImplemented
        self.__con__.commit()

    def close(self):
        self.__cur__.close()
        self.__con__.close()


if __name__ == "__main__":
    try:
        c1 = Course("234.345", "WS22", "KV", "Course1", [], "c1.live.com")
        c2 = Course("234.346", "WS22", "KV", "Course2", [], "c2.evil.com")
        student = Student("lel", "evil.org", {c1, c2}, "k12345678")
        db = Database()
        db.insert(student)
        db.close()
    except sqlite3.OperationalError as err:
        print(f"[{err.sqlite_errorname}]\t{err.args[0]}")
