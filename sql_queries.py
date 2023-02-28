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
                         "student_courses(discord_id, lva_nr, semester, active) " \
                         "VALUES (?,?,?,?)"

insert_course_teacher = "REPLACE INTO " \
                        "course_teacher(teacher_name, semester, lva_nr) " \
                        "VALUES (?,?,?)"

insert_class = "REPLACE INTO " \
               "class(lva_nr, semester, start_time, end_time, location) " \
               "VALUES (?,?,?,?,?)"

insert_roles = "REPLACE INTO " \
               "roles(lva_name, semester, guild_id, role_id, channel_id) " \
               "VALUES (?,?,?,?,?)"

insert_category = "REPLACE INTO " \
                  "category(guild_id, category_id) " \
                  "VALUES (?,?)"

toggle_active = "UPDATE student_courses " \
                "SET (active) = (?) " \
                "WHERE (discord_id, lva_nr, semester) = (?,?,?)"

delete_student = "DELETE FROM student WHERE discord_id = ?"

delete_role = "DELETE FROM roles WHERE (guild_id, role_id) = (?,?)"

delete_student_course = "DELETE FROM student_courses WHERE (discord_id, lva_nr, semester) = (?,?,?)"

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
                         "active BOOLEAN NOT NULL, " \
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
               "lva_name TEXT NOT NULL," \
               "semester TEXT NOT NULL," \
               "guild_id TEXT NOT NULL," \
               "role_id TEXT NOT NULL," \
               "channel_id TEXT NOT NULL," \
               "PRIMARY KEY (lva_name, semester, guild_id)" \
               ")"

create_categories = "CREATE TABLE IF NOT EXISTS category(" \
                    "guild_id TEXT NOT NULL," \
                    "category_id TEXT NOT NULL," \
                    "PRIMARY KEY (guild_id)" \
                    ")"

select_category_by_guild = "SELECT category_id " \
                           "FROM category " \
                           "WHERE (guild_id) = (?)"

select_role_by_id = "SELECT * " \
                    "FROM roles " \
                    "WHERE (guild_id, role_id) = (?,?)"

select_role_students = "SELECT discord_id " \
                       "FROM student_courses " \
                       "LEFT JOIN course " \
                       "    USING (lva_nr, semester) " \
                       "INNER JOIN roles " \
                       "    USING (lva_name, semester) " \
                       "WHERE (guild_id, role_id) = (?,?) " \
                       "AND active = TRUE"

select_student_courses = "SELECT c.* " \
                         "FROM student_courses " \
                         "LEFT JOIN course c " \
                         "  USING (lva_nr, semester) " \
                         "WHERE (discord_id, student_courses.semester) = (?,?)"

select_course = "SELECT * " \
                "FROM course " \
                "WHERE (lva_nr, semester) = (?,?)"

select_channel_by_lva = "SELECT channel_id " \
                        "FROM roles " \
                        "WHERE (guild_id, lva_name, semester) = (?,?,?)"

select_role_and_channel_by_lva = "SELECT role_id, channel_id " \
                                 "FROM roles " \
                                 "WHERE (guild_id, lva_name, semester) = (?,?,?)"

select_guild_channels = "SELECT channel_id " \
                        "FROM roles " \
                        "WHERE (guild_id) = (?)"

select_student_courses_by_lva = "SELECT sc.* " \
                                "FROM student_courses sc " \
                                "LEFT JOIN course " \
                                "   USING (lva_nr, semester)" \
                                "WHERE (lva_name, semester) = (?,?)"

select_discord_ids = "SELECT discord_id FROM student"

select_student_id = "SELECT student_id " \
                    "FROM student " \
                    "WHERE (discord_id) = (?)"

select_server_courses = "SELECT lva_name " \
                        "FROM roles " \
                        "WHERE (guild_id, semester) = (?,?)"

select_active = "SELECT active " \
                "FROM student_courses " \
                "WHERE (discord_id, lva_nr, semester) = (?,?,?)"

select_lva_nr = "SELECT lva_nr " \
                "FROM course " \
                "WHERE (lva_name, semester) = (?,?)"

select_lva_name_by_role_id = "SELECT lva_name " \
                             "FROM roles " \
                             "WHERE (semester, guild_id, role_id) = (?,?,?)"

select_lva_name_by_channel_id = "SELECT lva_name " \
                                "FROM roles " \
                                "WHERE (semester, guild_id, channel_id) = (?,?,?)"

select_channel_id = "SELECT channel_id " \
                    "FROM roles " \
                    "WHERE (guild_id, role_id) = (?,?)"

select_student_courses_by_id = "SELECT sc.lva_nr " \
                               "FROM student_courses as sc LEFT JOIN course as c " \
                               "WHERE sc.lva_nr = c.lva_nr " \
                               "AND sc.semester = c.semester " \
                               "AND (discord_id, sc.semester,lva_name) = (?,?,?)"

is_kusss = "SELECT student.* " \
           "FROM student " \
           "WHERE discord_id = ?"

is_managed_channel = "SELECT roles.* " \
                     "FROM roles " \
                     "WHERE channel_id = ?"

select_link = "SELECT calendar_link " \
              "FROM student " \
              "WHERE discord_id = ?"
