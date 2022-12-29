"""
    File name: kusss.py
    Author: Adrian Vinojcic
    This part is responsible for fetching users calendars.
"""

from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests
from icalendar import Calendar

__kusss__ = "www.kusss.jku.at"
__calendar_path__ = "/kusss/published-calendar.action"
__TOKEN__ = "token"
__lang__ = "de"

courses = []  # TODO: fill with data from database on bootup


def data_structure(link: str):
    i_calendar = calendar(link)
    cal = Calendar.from_ical(i_calendar)
    for component in cal.walk():
        if component.name == "VEVENT":
            summary: str = component.get('summary')
            summary_list = summary.split(" / ")

            # delete tag of exams
            if len(summary_list) > 3:
                summary_list = summary_list[1:]

            lva_type = summary_list[0][:2]
            lva_name = summary_list[0][3:]
            teacher = summary_list[1]
            lva_nr = summary_list[2][1:7]
            semester = summary_list[2][8:13]

            start: datetime = component.get('dtstart').dt
            end: datetime = component.get('dtend').dt
            location: str = component.get('location')


def calendar(link: str):
    _, content = __token_and_content__(link)
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
    link = "https://{}{}?{}={}&lang={}".format(__kusss__, __calendar_path__, __TOKEN__, user_token, __lang__)
    content = requests.get(link).content
    if len(content) == 0:
        raise InvalidURLException(link, "Token malformed or deprecated.")
    return user_token, content


class InvalidURLException(Exception):
    """Exception raised for invalid calendar links provided by the user."""

    def __init__(self, link: str, message="Provided link is not valid"):
        self.message = message
        self.link = link
        super().__init__(self.message)


class Course:
    def __init__(self, lva_type: str, lva_name: str, teacher: str, lva_nr: str, semester: str):
        self.type = lva_type
        self.name = lva_name
        self.teacher = teacher
        self.lva_nr = lva_nr
        self.semester = semester


class Class:
    def __init__(self, start: datetime, end: datetime, course: Course, location: str):
        self.start = start
        self.end = end
        self.course = course
        self.location = location
