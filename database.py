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
        self.__cur__.execute(query.create_categories)

    def insert(self, obj):
        match obj:
            case Student():
                self.__cur__.execute(query.insert_student, obj.to_db_entry())
                self.__cur__.executemany(
                    query.insert_student_courses,
                    [(obj.discord_id, course.lva_nr, course.semester) for course in obj.courses])
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

    def delete_roles(self, guild_id: str, role_ids: set[str]):
        selection = list(zip([guild_id] * len(role_ids), role_ids))
        self.__cur__.executemany(query.delete_role, selection)
        self.__con__.commit()

    def is_managed_role(self, guild_id: str, role_id: str) -> bool:
        result = list(self.__cur__.execute(query.select_role_by_id, (guild_id, role_id)))
        return len(result) >= 1

    # def is_managed_course(self, guild_id: str, lva_nr: str, semester: str) -> bool:
    #     result = list(self.__cur__.execute(query.select_role_by_lva, (lva_nr, semester, guild_id)))
    #     return len(result) > 0

    def is_needed_course(self, lva_name: str, semester: str) -> bool:
        result = list(self.__cur__.execute(query.select_student_courses_by_lva, (lva_name, semester)))
        return len(result) > 0

    def get_role_members(self, guild_id: str, role_id: str) -> set:
        result = self.__cur__.execute(query.select_role_students, (guild_id, role_id))
        return {entry[0] for entry in result}

    def get_added_courses(self, discord_id: str, semester: str) -> set[Course]:
        result = {Course(*elem[0:4], teachers=[], link=elem[4])
                  for elem in self.__cur__.execute(query.select_student_courses, (discord_id, semester))}
        return result

    def get_course(self, lva_nr: str, semester: str) -> Course:
        result = list(self.__cur__.execute(query.select_course, (lva_nr, semester)))[0]
        return Course(*result[0:4], teachers=[], link=result[4])

    # def get_role(self, lva_nr: str, semester: str, guild_id: str) -> str:
    #     result = list(self.__cur__.execute(query.select_role_by_lva, (lva_nr, semester, guild_id)))
    #     return result[0][0]

    def get_channel(self, guild_id: str, lva_name: str, semester: str) -> str:
        result = list(self.__cur__.execute(query.select_channel_by_lva, (guild_id, lva_name, semester)))
        return result[0][0]

    def get_role_and_channel(self, guild_id: str, lva_name: str, semester: str):
        result = list(self.__cur__.execute(query.select_role_and_channel_by_lva, (guild_id, lva_name, semester)))
        return result[0]

    def has_category(self, guild_id: str) -> bool:
        result = list(self.__cur__.execute(query.select_category_by_guild, (guild_id,)))
        return len(result) > 0

    def get_category(self, guild_id: str):
        result = list(self.__cur__.execute(query.select_category_by_guild, (guild_id,)))
        return result[0][0]

    def set_cagegory(self, guild_id: str, category_id: str):
        self.__cur__.execute(query.insert_category, (guild_id, category_id))

    def get_student_ids(self):
        result = self.__cur__.execute(query.select_discord_ids)
        return {entry[0] for entry in result}

    def get_matr_nr(self, discord_id: str):
        result = list(self.__cur__.execute(query.select_student_id, (discord_id,)))
        if len(result) == 0:
            return "No matriculation number saved!"
        return result[0][0]

    def get_server_courses(self, guild_id: str, semester: str):
        result = {elem[0] for elem in self.__cur__.execute(query.select_server_courses, (guild_id, semester))}
        return result

    def close(self):
        self.__cur__.close()
        self.__con__.close()
