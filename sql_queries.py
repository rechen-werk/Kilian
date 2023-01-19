"""
    File name: sql_queries.py
    Author: Tobias Pilz
    This file contains all queries for database.py.
"""
import database

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
               "roles(guild_id, role_id, lva_nr, semester) " \
               "VALUES (?,?,?,?)"

delete_student = "DELETE FROM student WHERE discord_id = ?"

create_student = "CREATE TABLE IF NOT EXISTS student(" \
                 "discord_id text not null, " \
                 "student_id text, " \
                 "calendar_link text not null," \
                 "primary key (discord_id)" \
                 ")"

create_course = "CREATE TABLE IF NOT EXISTS course(" \
                "lva_nr text not null, " \
                "semester text not null, " \
                "lva_type text not null , " \
                "lva_name text not null , " \
                "link text not null, " \
                "primary key (lva_nr, semester)" \
                ")"

create_student_courses = "CREATE TABLE IF NOT EXISTS student_courses(" \
                         "discord_id text not null, " \
                         "semester text not null, " \
                         "lva_nr text not null, " \
                         "primary key (discord_id, semester, lva_nr)," \
                         "CONSTRAINT fk_student" \
                         "  foreign key (discord_id) references student" \
                         "  ON DELETE CASCADE," \
                         "foreign key (lva_nr, semester) references course" \
                         ")"

create_course_teacher = "CREATE TABLE IF NOT EXISTS course_teacher(" \
                        "teacher_name text not null, " \
                        "semester text not null," \
                        "lva_nr integer not null, " \
                        "primary key (teacher_name, semester, lva_nr)," \
                        "foreign key (lva_nr, semester) references course" \
                        ")"

create_class = "CREATE TABLE IF NOT EXISTS class(" \
               "lva_nr text not null, " \
               "semester text not null, " \
               "start_time integer not null, " \
               "end_time integer not null, " \
               "location text not null," \
               "primary key (lva_nr, semester, start_time, end_time, location)," \
               "foreign key (lva_nr, semester) references course" \
               ")"

create_roles = "CREATE TABLE IF NOT EXISTS roles(" \
               "guild_id text not null," \
               "role_id text not null," \
               "lva_nr text not null," \
               "semester text not null," \
               "primary key (guild_id, role_id)," \
               "foreign key (lva_nr, semester) references course" \
               ")"

select_role = "SELECT * FROM roles " \
              "WHERE (guild_id, role_id) = (?,?)"

select_role_students = "SELECT discord_id FROM " \
                       "student_courses INNER JOIN " \
                       "roles r on " \
                       "student_courses.lva_nr = r.lva_nr and " \
                       "student_courses.semester = r.semester " \
                       "WHERE (guild_id, role_id) = (?,?)"

if __name__ == '__main__':
    db = database.Database()
    guild_id = "1013474125609701447"
    role_id = "1054843641836867695"
    if db.is_managed_role(guild_id, role_id):
        result = db.get_role_members(guild_id, role_id)
        for entry in result:
            print(entry)
