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


def calendar(url: str):
    url = urlparse(url)
    if url.netloc == kusss and url.path == calendar_path:
        token = parse_qs(url.query)[TOKEN][0]
        url = "https://{}{}?token={}&lang={}".format(kusss, calendar_path, token, lang)
        return token, requests.get(url).content
    else:
        raise
