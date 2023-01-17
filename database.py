"""
    File name: database.py
    Author:
    This part is responsible for everything related to the database.
"""
import sqlite3

from kusss import Student, Course, Class

__DB__ = "discord.db"

__insert_student_query__ = "INSERT INTO " \
                           "student(discord_id, calendar_link, courses, student_id) " \
                           "VALUES (?,?,?,?)"

__insert_course_query__ = "INSERT INTO " \
                          "course(lva_nr, semester, lva_type, lva_name, teachers, link) " \
                          "VALUES (?,?,?,?)"

__insert_class_query__ = "INSERT INTO " \
                         "class(lva_nr, semester, start_time, end_time, location) " \
                         "VALUES (?,?,?,?)"


class Database:
    def __init__(self):
        self.__con__ = sqlite3.connect(__DB__)
        self.__cur__ = self.__con__.cursor()
        self.__create_tables__()

    def __create_tables__(self):
        self.__cur__.execute("CREATE TABLE student(discord_id primary key, calendar_link, courses, student_id)")
        self.__cur__.execute("CREATE TABLE course(lva_nr primary key, semester, lva_type, lva_name, teachers, link)")
        self.__cur__.execute("CREATE TABLE class(lva_nr primary key, semester, start_time, end_time, location)")

    def insert(self, obj):
        if isinstance(obj, Student):
            self.__cur__.execute(__insert_student_query__, obj.to_db_entry())
        elif isinstance(obj, Course):
            self.__cur__.execute(__insert_course_query__, obj.to_db_entry())
        elif isinstance(obj, Class):
            self.__cur__.execute(__insert_class_query__, obj.to_db_entry())
        else:
            return
        self.__con__.commit()

    def close(self):
        self.__cur__.close()
        self.__con__.close()


if __name__ == "__main__":
    try:
        student = Student("disc_id", "link.com", set(), "k12345678")
        db = Database()
        db.insert(student)
        db.close()
    except sqlite3.OperationalError as err:
        print(f"[{err.sqlite_errorname}]\t{err.args[0]}")
