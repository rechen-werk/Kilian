"""
    File name: sql_queries.py
    Author: Tobias Pilz
    This file contains all queries for database.py.
"""

insert_student = "REPLACE INTO " \
                 "student(discord_id, student_id, calendar_link) " \
                 "VALUES (?,?,?)"

insert_course = "REPLACE INTO " \
                "course(lva_nr, semester, lva_type, lva_name, link) " \
                "VALUES (?,?,?,?,?)"

insert_student_courses = "REPLACE INTO " \
                         "student_courses(discord_id, lva_nr, semester) " \
                         "VALUES (?,?,?)"

insert_course_teacher = "REPLACE INTO " \
                        "course_teacher(teacher_name, semester, lva_nr) " \
                        "VALUES (?,?,?)"

insert_class = "REPLACE INTO " \
               "class(lva_nr, semester, start_time, end_time, location) " \
               "VALUES (?,?,?,?,?)"

insert_roles = "REPLACE INTO " \
               "roles(lva_nr, semester, guild_id, role_id, channel_id) " \
               "VALUES (?,?,?,?,?)"

delete_student = "DELETE FROM student WHERE discord_id = ?"

delete_role = "DELETE FROM roles WHERE (guild_id, role_id) = (?,?)"

create_student = "CREATE TABLE IF NOT EXISTS student(" \
                 "discord_id TEXT NOT NULL, " \
                 "student_id TEXT, " \
                 "calendar_link TEXT NOT NULL, " \
                 "PRIMARY KEY (discord_id)" \
                 ")"

create_course = "CREATE TABLE IF NOT EXISTS course(" \
                "lva_nr TEXT NOT NULL, " \
                "semester TEXT NOT NULL, " \
                "lva_type TEXT NOT NULL, " \
                "lva_name TEXT NOT NULL, " \
                "link TEXT NOT NULL, " \
                "PRIMARY KEY (lva_nr, semester)" \
                ")"

create_student_courses = "CREATE TABLE IF NOT EXISTS student_courses(" \
                         "discord_id TEXT NOT NULL, " \
                         "semester TEXT NOT NULL, " \
                         "lva_nr TEXT NOT NULL, " \
                         "PRIMARY KEY (discord_id, semester, lva_nr)," \
                         "CONSTRAINT fk_student" \
                         "  FOREIGN KEY (discord_id) REFERENCES student" \
                         "  ON DELETE CASCADE," \
                         "FOREIGN KEY (lva_nr, semester) REFERENCES course" \
                         ")"

create_course_teacher = "CREATE TABLE IF NOT EXISTS course_teacher(" \
                        "teacher_name TEXT NOT NULL, " \
                        "semester TEXT NOT NULL, " \
                        "lva_nr INTEGER NOT NULL, " \
                        "PRIMARY KEY (teacher_name, semester, lva_nr)," \
                        "FOREIGN KEY (lva_nr, semester) REFERENCES course" \
                        ")"

create_class = "CREATE TABLE IF NOT EXISTS class(" \
               "lva_nr TEXT NOT NULL, " \
               "semester TEXT NOT NULL, " \
               "start_time INTEGER NOT NULL, " \
               "end_time INTEGER NOT NULL, " \
               "location TEXT NOT NULL, " \
               "PRIMARY KEY (lva_nr, semester, start_time, end_time, location)," \
               "FOREIGN KEY (lva_nr, semester) REFERENCES course" \
               ")"

create_roles = "CREATE TABLE IF NOT EXISTS roles(" \
               "lva_nr TEXT NOT NULL," \
               "semester TEXT NOT NULL," \
               "guild_id TEXT NOT NULL," \
               "role_id TEXT NOT NULL," \
               "channel_id TEXT NOT NULL," \
               "PRIMARY KEY (lva_nr, semester, guild_id)," \
               "FOREIGN KEY (lva_nr, semester) REFERENCES course" \
               ")"

select_role_by_id = "SELECT * " \
                    "FROM roles " \
                    "WHERE (guild_id, role_id) = (?,?)"

select_role_students = "SELECT discord_id " \
                       "FROM student_courses " \
                       "INNER JOIN roles r ON " \
                       "student_courses.lva_nr = r.lva_nr " \
                       "AND " \
                       "student_courses.semester = r.semester " \
                       "WHERE (guild_id, role_id) = (?,?)"

select_student_courses = "SELECT lva_nr, semester " \
                         "FROM student_courses " \
                         "WHERE discord_id = (?)"

select_course = "SELECT * " \
                "FROM course " \
                "WHERE (lva_nr, semester) = (?,?)"

select_role_by_lva = "SELECT role_id " \
                     "FROM roles " \
                     "WHERE (lva_nr, semester, guild_id) = (?,?,?)"

select_channel_by_lva = "SELECT channel_id " \
                        "FROM roles " \
                        "WHERE (guild_id, lva_nr, semester) = (?,?,?)"

select_guild_channels = "SELECT channel_id " \
                        "FROM roles " \
                        "WHERE (guild_id) = (?)"

select_student_courses_by_lva = "SELECT * " \
                                "FROM student_courses " \
                                "WHERE (lva_nr, semester) = (?,?)"

select_discord_ids = "SELECT discord_id FROM student"
