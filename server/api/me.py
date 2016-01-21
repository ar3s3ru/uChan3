# Flask related imports
# API related imports
from server import uchan
from server.api import handler
from server.api import AuthEntity
from server.models import User
from server.common import responses
from server.common import JSONRepresentation


class Me(AuthEntity):
    """
    API Resource entity for 'me' resource.
    It's used to retrieve user-specific informations, so it needs to be subclassed from AuthEntity class.
    """

    @handler
    def get(self):
        """
        GET method implementation for Me API resource entity.

        :return: JSON response (200 OK, 404 Not Found, 401 Unauthorized)
        """
        def routine(user: User):
            return responses.successful(200, JSONRepresentation.me(user))

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
            return responses.successful(200, [JSONRepresentation.thread(thread, user)
                                              for thread in user.get_threads(page)])

        return self.session_oriented_request(routine)

uchan.api.add_resource(Me, '/api/me')
uchan.api.add_resource(MeThreads, '/api/me/threads', '/api/me/threads/<int:page>')
