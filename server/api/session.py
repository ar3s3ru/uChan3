from uuid import uuid4
# Flask related imports
from flask import request, Request
from sqlalchemy.exc import IntegrityError
# API related imports
from server import uchan
from server.api import BasicEntity
from server.api import handler, handler_data, handler_args
from server.api.me import Me
from server.models import User, Session
from server.common import responses
from server.common.routines import is_valid_nick, is_valid_pass, hashing_password


class SessionAPI(BasicEntity):
    """
    API Session resource.
    Subclassed from BasicEntity, no OAuth mechanisms.

    It uses POST and DELETE methods, with JSON arguments included in __init__ constructor.
    """

    def __init__(self):
        """
        Construct the Session resource entity.

        Calls the BasicEntity superclass for headers parsing, and adds the desired request body parsing
        for POST method.

        :return: Session resource object
        """
        super().__init__()

        self.form.add_argument('nickname', type=str, location='json')
        self.form.add_argument('password', type=str, location='json')

    @handler_args
    def validate_args(self):
        """
        Check if all required arguments are valid.

        :return: Raises ValueError if some required arguments are invalid, else nothing
        """
        if not is_valid_nick(self.args['nickname']):
            raise ValueError('Invalid parameter: nickname')
        elif not is_valid_pass(self.args['password']):
            raise ValueError('Invalid parameter: password')

    @staticmethod
    def generate_token():
        """
        Generates new session token for authorization.

        :return: New random UUID token for authorization
        """
        return str(uuid4())

    @staticmethod
    def retrieve_session(token: str):
        """
        Retrieve Session table object from token.

        :param token: Authorization token
        :return: Session object related to authorization token
        """
        return Session.query.filter_by(token=token).first()

    @handler_args
    def retrieve_user_nickname(self):
        """
        Retrieve User table object from nickname.

        :return: User object with specified nickname
        """
        return User.query.filter_by(nickname=self.args['nickname']).first()

    @handler_args
    def register_session(self, request: Request):
        """
        Construct new Session object from POST fields.

        :param request: HTTP request
        :return: Session object and related User object
        """
        ip_addr = request.remote_addr
        user    = self.retrieve_user_nickname()

        if user is None or user.password != hashing_password(user.salt, self.args['password']):
            raise ValueError('Invalid login')

        return Session(ip_addr, self.generate_token(), user.id), user

    @handler_data
    def post(self):
        """
        POST method implementation for API Session resource entity.

        :return: JSON response (201 Created, 400 Bad Request, 409 Conflict [Database IntegrityError])
        """
        try:
            self.check_args()
            self.validate_args()

            session, user = self.register_session(request)

            uchan.add_to_db(session)
            return responses.successful(201, {'token': session.token, 'user': Me.me_user_representation(user)})
        except ValueError as msg:
            # Arguments validation error
            return responses.client_error(400, '{}'.format(msg))
        except IntegrityError as msg:
            # Database integrity error
            return responses.client_error(409, 'Session error, check your JSON or contact server manteiner'
                                          .format(msg))

    @handler
    def delete(self, token: str):
        """
        DELETE method implementation for API Session resource entity.

        :param token: Requested token to delete (from URL)
        :return: JSON response (204 No Content, 404 Not Found)
        """
        session = self.retrieve_session(token)

        if session is None:
            return responses.client_error(404, 'Token not found')

        uchan.delete_from_db(session)
        return '', 204

uchan.api.add_resource(SessionAPI, '/api/session', '/api/session/<token>')
