"""
    File name: kusss.py
    Author: Adrian Vinojcic
    This part is responsible for fetching users calendars.
"""

from io import StringIO
# from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests
from icalendar import Calendar
from lxml import html
import pandas

__kusss__ = "www.kusss.jku.at"
__calendar_path__ = "/kusss/published-calendar.action"
__TOKEN__ = "token"
__lang__ = "de"


def all_courses():
    content = requests.get("https://kusss.jku.at/kusss/coursecatalogue-search-lvas.action?").content
    table = html.fromstring(content).xpath("/html/body/table/tr[2]/td[2]/table/tr[2]/td/div/table[2]")[0]
    table_string = html.tostring(table).decode()
    df = pandas.read_html(StringIO(table_string), decimal=",", thousands=".")[0]
    # df.to_csv("2022.csv", decimal=",", sep=";", index=False)
    kusss_courses = set()
    for _, row in df.iterrows():
        kusss_courses.add(Course(lva_type=row["Typ"], lva_name=row["LVA-Titel"], teacher=row["LeiterIn"], lva_nr=row["LVA-Nr."], semester=row["Sem."]))
    return kusss_courses


def courses(user_token: str):
    user_courses = set()
    i_calendar = __calendar__(user_token)
    cal = Calendar.from_ical(i_calendar)
    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary').split(" / ")

            # delete tag of exams
            if len(summary) > 3:
                summary = summary[1:]

            user_courses.add(
                Course(
                    lva_type=summary[0][:2],
                    lva_name=summary[0][3:],
                    teacher=summary[1],
                    lva_nr=summary[2][1:7],
                    semester=summary[2][8:13]
                )
            )

            # parse data for timetable
            # start: datetime = component.get('dtstart').dt
            # end: datetime = component.get('dtend').dt
            # location: str = component.get('location')
    return user_courses


def __calendar__(user_token: str):
    _, content = __token_and_content__(f"https://{__kusss__}{__calendar_path__}?{__TOKEN__}={user_token}&lang={__lang__}")
    return content


def token(link: str):
    user_token, _ = __token_and_content__(link)
    return user_token


def __token_and_content__(link: str):
    url = urlparse(link)
    if url.netloc != __kusss__ or url.path != __calendar_path__:
        raise InvalidURLException(link, "Invalid URL.")

    try:
        user_token = parse_qs(url.query)[__TOKEN__][0]
    except Exception:
        raise InvalidURLException(link, "Token not in query.")
    link = f"https://{__kusss__}{__calendar_path__}?{__TOKEN__}={user_token}&lang={__lang__}"
    content = requests.get(link).content
    if len(content) == 0:
        raise InvalidURLException(link, "Token malformed or deprecated.")
    return user_token, content


class InvalidURLException(Exception):
    """Exception raised for invalid calendar links provided by the user."""

    def __init__(self, link: str, message="Provided link is not valid"):
        self.message = message + " You can get your link from https://www.kusss.jku.at/kusss/ical-multi-form-sz.action."
        self.link = link
        super().__init__(self.message)


class Course:
    def __init__(self, lva_type: str, lva_name: str, teacher: str, lva_nr: str, semester: str):
        self.type = lva_type
        self.name = lva_name
        self.teacher = teacher
        self.lva_nr = lva_nr
        self.semester = semester

    def __eq__(self, other):
        return isinstance(other, Course) and self.lva_nr == other.lva_nr and self.semester == other.semester

    def __ne__(self, other):
        return not __eq__(other)

    def __hash__(self):
        return hash(self.lva_nr + self.semester)

# Class data structure for timetables later eventually
# class Class:
#    def __init__(self, start: datetime, end: datetime, course: Course, location: str):
#        self.start = start
#        self.end = end
#        self.course = course
#        self.location = location
