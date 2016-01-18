#!flask/bin/python
from sys import argv
from server import uchan
from server.models import User, Board, UserBoard

help = """
    Usage: update_boards.py [memo board] [name board]
"""

if __name__ == '__main__' and len(argv) == 3:
    memo = argv[1]
    name = argv[2]

    uchan.add_to_db(Board(memo, name, 1))
    board = Board.query.order_by(Board.id.desc()).first()

    for user in User.query.all():
        uchan.add_to_db(UserBoard(user.id, board.id), False)

    uchan.commit()

else:
    print(help)
