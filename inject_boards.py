#!flask/bin/python
from server import uchan
from server.models import Board
from flask import json

with open('boards.json', 'r') as general_boards:
    boards_list = json.load(general_boards)

for board in boards_list:
    memo = board['memo']
    name  = board['name']

    x = Board(memo, name, 1)
    uchan.add_to_db(x, False)

uchan.commit()
