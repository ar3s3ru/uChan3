# Flask related imports
from flask_restful import Resource
# API related imports
from server import uchan
from server.common import responses
from server.models import User, Board, UserBoard


class Activation(Resource):
    """
    API Activation resource entity.

    Since activation is done via browser (link from email), we cannot use API-specific resource classes.
    This class will only use GET method.
    """
    @staticmethod
    def retrieve_user_by_token(token: str):
        """
        Queries platform database and retrieve user table entry with specified activation token.

        :param token: Activation token
        :return: User bind to specified token
        """
        return User.query.filter_by(token=token).first()

    @staticmethod
    def add_to_general_boards(user: User):
        """
        Adds specified user to general boards (university.id = 1).

        :param user: User activating object
        :return: Nothing
        """
        for board in Board.query.filter_by(university=1).all():
            uchan.add_to_db(UserBoard(user.id, board.id), False)

    @staticmethod
    def add_to_university_board(user: User):
        """
        Adds specified user to its university board.

        :param user: User activating object
        :return: Nothing
        """
        board = Board.query.filter_by(university=user.university).first()
        if board is not None:
            uchan.add_to_db(UserBoard(user.id, board.id), False)

    def get(self, token: str):
        """
        GET method implementation for API Activation resource entity.

        :param token: Activation token from URL
        :return: JSON Response (200 OK, 404 Not Found, 409 Conflict)
        """
        user = self.retrieve_user_by_token(token)

        if user is None:
            return responses.client_error(404, 'Invalid token')

        if user.activated:
            return responses.client_error(409, 'User already activated')

        # Activate user and add it to boards
        user.activated = True
        self.add_to_general_boards(user)
        self.add_to_university_board(user)

        uchan.commit()
        return responses.successful(200, 'User {} activated'.format(user.nickname))

uchan.api.add_resource(Activation, '/api/activation/<token>')
