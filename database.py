"""
    File name: database.py
    Author: Tobias Pilz
    This part is responsible for everything related to the database.
"""
import sqlite3

import kusss
import sql_queries as query
from kusss import Student, Course, Class

__DB__ = "discord.db"


class Roles(set):
    pass


class Database:
    def __init__(self):
        self.__con__ = sqlite3.connect(__DB__)
        self.__cur__ = self.__con__.cursor()
        self.__cur__.execute("PRAGMA foreign_keys = ON")
        self.__create_tables__()
        self.refresh()

    def refresh(self):
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
        match obj:
            case Student():
                self.__cur__.execute(query.insert_student, obj.to_db_entry())
                self.__cur__.executemany(query.insert_student_courses, [(obj.discord_id, course.lva_nr, course.semester) for course in obj.courses])
            case Course():
                self.__cur__.execute(query.insert_course, obj.to_db_entry())
            case Class():
                self.__cur__.execute(query.insert_class, obj.to_db_entry())
            case Roles():
                self.__cur__.executemany(query.insert_roles, obj)
            case _:
                return NotImplemented
        self.__con__.commit()

    def delete_student(self, discord_id: str):
        self.__cur__.execute(query.delete_student, (discord_id,))
        self.__con__.commit()

    def delete_roles(self, guild_id: str, role_ids: {str}):
        selection = list(zip([guild_id] * len(role_ids), role_ids))
        self.__cur__.executemany(query.delete_role, selection)
        self.__con__.commit()

    def is_managed_role(self, guild_id: str, role_id: str) -> bool:
        result = list(self.__cur__.execute(query.select_role_by_id, (guild_id, role_id)))
        return len(result) >= 1

    def is_managed_course(self, guild_id: str, lva_nr: str, semester: str) -> bool:
        result = list(self.__cur__.execute(query.select_role_by_lva, (lva_nr, semester, guild_id)))
        return len(result) > 0

    def is_needed_course(self, lva_nr: str, semester: str) -> bool:
        result = list(self.__cur__.execute(query.select_student_courses_by_lva, (lva_nr, semester)))
        return len(result) > 0

    def get_role_members(self, guild_id: str, role_id: str) -> set:
        result = self.__cur__.execute(query.select_role_students, (guild_id, role_id))
        return {entry[0] for entry in result}

    def get_added_courses(self, discord_id: str) -> set:
        result = set(self.__cur__.execute(query.select_student_courses, (discord_id,)))
        return result

    def get_course(self, lva_nr: str, semester: str) -> Course:
        result = list(self.__cur__.execute(query.select_course, (lva_nr, semester)))[0]
        return Course(*result[0:4], teachers=[], link=result[4])

    def get_role(self, lva_nr: str, semester: str, guild_id: str) -> str:
        result = list(self.__cur__.execute(query.select_role_by_lva, (lva_nr, semester, guild_id)))
        return result[0][0]

    def get_student_ids(self):
        result = self.__cur__.execute(query.select_discord_ids)
        return {entry[0] for entry in result}

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
