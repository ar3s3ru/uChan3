#!flask/bin/python
from flask import json
from server import uchan
from server.models import University


with open('universities.json', 'r') as uni_file:
    uni_list = json.load(uni_file)

nouni = University('NONAME', 'NOCITY', 'NODOMAIN', '')
uchan.db.session.add(nouni)

for uni in uni_list:
    n = uni['name']
    d = uni['mailDomain']
    c = uni['city']
    try:
        s = uni['mailSuggestion']
    except KeyError:
        s = ""

    el = University(n, c, d, s)
    uchan.db.session.add(el)

uchan.db.session.commit()
