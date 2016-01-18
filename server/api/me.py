# Flask related imports
# API related imports
from server import uchan
from server.api import handler
from server.api import AuthEntity
from server.api.thread import ThreadAPI
from server.api.university import UniversityAPI
from server.models import User, Board
from server.common import responses


class Me(AuthEntity):
    """
    API Resource entity for 'me' resource.
    It's used to retrieve user-specific informations, so it needs to be subclassed from AuthEntity class.
    """

    @staticmethod
    def me_board_representation(board: Board):
        """
        Board object representation ready for JSON serialization.

        :param board: Board object
        :return: Dictionary with Board representation fields
        """
        return {'id': board.id, 'memo': board.memo, 'name': board.name}

    @staticmethod
    def me_user_representation(user: User):
        """
        User object representation ready for JSON serialization.

        :param user: User object
        :return: Dictionary with User representation fields
        """
        return {
            'id':         user.id,
            'nickname':   user.nickname,
            'university': UniversityAPI.university_id(user.university).name,
            'gender':     user.get_gender(),
            'boards':     [Me.me_board_representation(board) for board in user.get_boards()]
        }

    @handler
    def get(self):
        """
        GET method implementation for Me API resource entity.

        :return: JSON response (200 OK, 404 Not Found, 401 Unauthorized)
        """
        def routine(user: User):
            return responses.successful(200, Me.me_user_representation(user))

        return self.session_oriented_request(routine)


class MeThreads(AuthEntity):
    """
    API Resource entity for 'me' resource.
    It's used to retrieve user-specific informations, so it needs to be subclassed from AuthEntity class.

    This is used to retrieve threads submitted by authorized user.
    """
    @handler
    def get(self, page=1):
        """
        GET method implementation for MeThreads API resource entity.

        :param page: Page requested for thread paginated query
        :return: JSON response (200 OK, 404 Not Found, 401 Unauthorized)
        """
        def routine(user: User):
            # TODO: update this with Thread shit
            return responses.successful(200,
                [ThreadAPI.thread_representation(thread, user) for thread in user.get_threads(page)])

        return self.session_oriented_request(routine)

uchan.api.add_resource(Me, '/api/me')
uchan.api.add_resource(MeThreads, '/api/me/threads', '/api/me/threads/<int:page>')
