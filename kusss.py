"""
    File name: kusss.py
    Author: Adrian Vinojcic
    This part is responsible for fetching users calendars.
"""
import datetime
from urllib.parse import urlparse, parse_qs
import requests
from icalendar import Calendar
from bs4 import BeautifulSoup


class InvalidURLException(Exception):
    """Exception raised for invalid calendar links provided by the user."""

    def __init__(self, link: str, message="Provided link is not valid"):
        self.message = message + " You can get your link from https://www.kusss.jku.at/kusss/ical-multi-form-sz.action."
        self.link = link
        super().__init__(self.message)


class CourseKey:
    def __init__(self, lva_nr: str, semester: str):
        self.lva_nr = lva_nr
        self.semester = semester

    def __eq__(self, other):
        return isinstance(other, CourseKey) and self.lva_nr == other.lva_nr and self.semester == other.semester

    def __ne__(self, other):
        return not __eq__(other)

    def __hash__(self):
        return hash(self.lva_nr + self.semester)

    def to_db_entry(self) -> tuple:
        return self.lva_nr, self.semester


class Class(CourseKey):
    def __init__(self, lva_nr: str, semester: str, start: datetime, end: datetime, location: str):
        super().__init__(lva_nr, semester)
        self.start = start
        self.end = end
        self.location = location

    def __eq__(self, other):
        return isinstance(other, Class) and \
            self.lva_nr == other.lva_nr and \
            self.semester == other.semester and \
            self.start == other.start and \
            self.end == other.end and \
            self.location == other.location

    def __ne__(self, other):
        return not __eq__(other)

    def __hash__(self):
        return hash(self.lva_nr + self.semester + self.location) ^ hash(self.start) ^ hash(self.end)

    def to_db_entry(self) -> tuple:
        return self.lva_nr, self.semester, self.start, self.end, self.location


class Course(CourseKey):
    def __init__(self, lva_nr: str, semester: str, lva_type: str, lva_name: str, teachers: list[str], link: str):
        super().__init__(lva_nr, semester)
        self.lva_type = lva_type
        self.lva_name = lva_name
        self.teachers = teachers
        self.link = link

    def classes(self) -> set[Class]:
        """Returns a set of all classes of the course."""
        all_classes = set[Class]()
        table = BeautifulSoup(requests.get(self.link).text, 'html.parser').findAll("table")[6]

        for row in table.find_all("tr")[1:-1:2]:
            cols = row.findAll("td")
            date = cols[1].text.strip()
            times = cols[2].text.strip().split(" – ")

            all_classes.add(Class(
                lva_nr=self.lva_nr,
                semester=self.semester,
                start=datetime.datetime.strptime(date + times[0], '%d.%m.%y%H:%M'),
                end=datetime.datetime.strptime(date + times[1], '%d.%m.%y%H:%M'),
                location=cols[3].text.strip()
            ))

        return all_classes

    def to_db_entry(self) -> tuple:
        return self.lva_nr, self.semester, self.lva_type, self.lva_name, self.link  # no teachers


class Student:
    def __init__(self, discord_id: str, calendar_link: str, courses: set[CourseKey], student_id: str = None):
        self.discord_id = discord_id
        self.calendar_link = calendar_link
        self.courses = courses
        self.student_id = student_id

    def __eq__(self, other):
        return isinstance(other, Student) and self.discord_id == other.discord_id

    def __ne__(self, other):
        return not __eq__(other)

    def __hash__(self):
        return hash(self.discord_id)

    def to_db_entry(self) -> tuple:
        return self.discord_id, self.student_id, self.calendar_link


def courses() -> set[Course]:
    """Returns a list of all Courses held at JKU in the current semester."""
    all_courses = set()

    table = BeautifulSoup(requests.get("https://kusss.jku.at/kusss/coursecatalogue-search-lvas.action?").text,
                          'html.parser').findAll("table")[5]

    for row in table.find_all("tr")[1:]:
        cols = row.findAll("td")
        all_courses.add(Course(
            lva_nr="".join(cols[0].text.strip().split(".")),
            semester=cols[5].text.strip(),
            lva_type=cols[2].text.strip(),
            lva_name=" ".join(cols[1].text.split()),
            teachers=list(map(lambda elem: elem.text.strip(), cols[4].findAll("a"))),
            link=f'www.kusss.jku.at/kusss/{cols[0].find("a")["href"].strip()}'
        ))

    return all_courses


def student(discord_id: str, link: str, student_id: str = None) -> Student:
    """Returns a student object with keys to all courses which are taken in the current semester."""
    url = urlparse(link)
    if url.netloc != "www.kusss.jku.at" or url.path != "/kusss/published-calendar.action":
        raise InvalidURLException(link, "Invalid URL.")

    try:
        user_token = parse_qs(url.query)["token"][0]
    except Exception:
        raise InvalidURLException(link, "Token not in query.")

    link = f"https://www.kusss.jku.at/kusss/published-calendar.action?token={user_token}&lang=de"

    i_calendar = requests.get(link).content
    if len(i_calendar) == 0:
        raise InvalidURLException(link, "Token malformed or deprecated.")

    cal = Calendar.from_ical(i_calendar)
    user_courses = set[CourseKey]()
    cur_sem = current_semester()
    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get('summary').split(" / ")

            # delete tag of exams
            if len(summary) > 3:
                summary = summary[1:]

            semester = summary[2][8:13]
            if semester == cur_sem:
                user_courses.add(CourseKey(
                    lva_nr=summary[2][1:7],
                    semester=semester
                ))

    return Student(
        discord_id=discord_id,
        calendar_link=link,
        courses=user_courses,
        student_id=student_id
    )


def current_semester() -> str:
    return BeautifulSoup(requests.get("https://www.kusss.jku.at/kusss/coursecatalogue-start.action").text,
                         'html.parser').find("option").text.strip()
