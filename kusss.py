"""
    File name: kusss.py
    Author: Adrian Vinojcic
    This part is responsible for fetching users calendars (and maybe interacting with the kusss api if there is one).
"""

from urllib.parse import urlparse, parse_qs
import requests

kusss = "www.kusss.jku.at"
calendar_path = "/kusss/published-calendar.action"
TOKEN = "token"
lang = "de"


def calendar(link: str):
    url = urlparse(link)
    if url.netloc != kusss or url.path != calendar_path:
        raise InvalidURLException(link, "Invalid URL.")

    try:
        token = parse_qs(url.query)[TOKEN][0]
    except Exception:
        raise InvalidURLException(link, "Token not in query.")

    link = "https://{}{}?{}={}&lang={}".format(kusss, calendar_path, TOKEN, token, lang)
    content = requests.get(link).content
    if len(content) == 0:
        raise InvalidURLException(link, "Token malformed.")
    return token, content


class InvalidURLException(Exception):
    """Exception raised for invalid calendar links provided by the user."""

    def __init__(self, link, message="Provided link is not valid"):
        self.message = message
        self.link = link
        super().__init__(self.message)
