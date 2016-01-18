# Flask related imports
# API related imports
from server import uchan
from server.api import AuthEntity
from server.api import handler, handler_data, handler_args
from server.common import responses
from server.models import User, Board
from server.api.me import ThreadAPI


class BoardAPI(AuthEntity):

    def __init__(self):
        super().__init__()

        self.form.add_argument('anon', type=str, location='json')
        self.form.add_argument('title', type=str, location='json')
        self.form.add_argument('text', type=str, location='json')
        self.form.add_argument('image', type=str, location='json')
        self.form.add_argument('image_name', type=str, location='json')

    @staticmethod
    def get_board(board_id: int):
        return Board.query.get(board_id)

    @handler
    def get(self, id: int, page=1):
        def routine(user: User):
            board = self.get_board(id)

            if board is None:
                return responses.client_error(404, 'Board does not exist')
            elif not user.board_subscribed(id):
                return responses.client_error(401, 'User is not authorized to see this board')

            return responses.successful(200, [ThreadAPI.thread_representation(thread, user)
                                              for thread in board.get_threads(page)])

        return self.session_oriented_request(routine)

    @handler_data
    def post(self, id: int):
        pass

uchan.api.add_resource(BoardAPI, '/api/board/<int:id>', '/api/board/<int:id>/<int:page>')
