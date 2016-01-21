# Python-lib and Flask related imports
from functools import wraps
from base64 import b64decode
from flask_restful import Resource, reqparse, request
# API related imports
from server.common import responses
from server.common.routines import get_user
from server.common.routines import new_filename, is_valid_file, decode_file
from server.models import Session


def handler(method):
    """
    Methods decorator for resource methods.
    It will check if required headers are correct.

    Please note, this method does not check for Content-Type header, so it will be needed for GET, HEAD, DELETE
    and OPTIONS HTTP requests.

    :param method: API resource method
    :return: 400 Bad Request error if required headers are not correct, else returns wrapped method
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if not self.check_headers():
            return responses.client_error(400, 'Wrong format request')
        else:
            return method(self, *args, **kwargs)
    return wrapped


def handler_data(method):
    """
    Methods decorator for resource methods.
    It will check if required headers are correct.

    Please note, this method checks for Content-Type header, so it will be needed for POST and PUT HTTP requests.

    :param method: API resource method
    :return: 400 Bad Request error if required headers are not correct, else returns wrapped method
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if not self.check_headers(True):
            return responses.client_error(400, 'Wrong format request')
        else:
            return method(self, *args, **kwargs)
    return wrapped


# TODO: ottimizza gli handler - eseguire una volta sola (definire un secondo decoratore ed un metodo che lo implementi)
def handler_args(method):
    """
    Method decorator for resource methods.
    It will check if required arguments are parsed.

    :param method: API resource method
    :return: Raises AssertionError if arguments have not been parsed, else returns wrapped method
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if self.args is None:
            raise AssertionError('Parsing argument is needed')
        else:
            return method(self, *args, **kwargs)
    return wrapped


class AuthException(Exception):
    """
    AuthEntity authorization exception.
    Intended to be used when there are errors using Authorization mechanisms.
    """
    def __init__(self, msg: str):
        self.msg = msg


class BasicEntity(Resource):
    """
    Basic API Resource entity.

    It assures basic headers checks using a RequestParser from Flask-RESTful framework.
    Any resource intended to be accessible from outside without an OAuth mechanism, needs to be
    subclassed from this class.
    """
    form    = reqparse.RequestParser()
    parser  = reqparse.RequestParser()
    headers = None
    args    = None
    clients = ['android', 'ios', 'windows']

    def __init__(self):
        """
        Construct the basic entity adding headers fields needed by RequestParser.

        Since we want to use custom error messages, they're not flagged as 'required', due to
        Flask-RESTful implementation, even if they need to be required as well.

        :return: New BasicEntity resource object
        """
        self.parser.add_argument('uChan-Client-Type', location='headers')
        self.parser.add_argument('uChan-Client-Version', location='headers')
        self.parser.add_argument('Accept', location='headers')
        self.parser.add_argument('Content-Type', location='headers')

    def check_headers(self, cont_type=False):
        """
        Parses basic headers and checks if headers values are correct.

        :param cont_type: Content-Type header flag, checked if it's set to True
        :return: If basic headers are correct
        """
        self.headers = self.parser.parse_args()

        if request.method in ['POST', 'PUT']:
            self.args = self.form.parse_args()

        uchan_type = self.headers['uChan-Client-Type']
        uchan_vers = self.headers['uChan-Client-Version']
        uchan_acc  = self.headers['Accept']
        uchan_cont = self.headers['Content-Type'] if cont_type else 'application/json'

        check_type = uchan_type is not None and uchan_type in self.clients
        check_vers = uchan_vers is not None
        check_acc  = uchan_acc  is not None and 'application/json' in uchan_acc
        check_cont = uchan_cont is not None and 'application/json' in uchan_cont

        return check_type and check_vers and check_acc and check_cont

    @handler_args
    def check_args(self):
        """
        Check if all required arguments have been included in request body.

        :return: Raises ValueError if some required arguments are missing, else nothing
        """
        for arg in self.args:
            if self.args[arg] is None:
                raise ValueError('Missing parameter: {}'.format(arg))


class AuthEntity(BasicEntity):
    """
    Authorization API entity, subclassed from BasicEntity.

    This entity marks an OAuth API Resource, hence it needs an additional 'Authorization' header.
    Thanks to OOP, this is quite self-explanatory.
    """
    def __init__(self):
        """
        Construct an AuthEntity object, adding to parser the 'Authorization' field.

        :return: New AuthEntity resource object
        """
        super().__init__()
        self.parser.add_argument('Authorization', location='headers')

    def check_headers(self, cont_type=False):
        """
        Checks basic headers calling the superclass, and then checks the integrity
        of the 'Authorization' header (base64 value).

        :param cont_type: Content-Type header flag, checked if it's set to True
        :return: If basic headers and Authorization header are correct
        """
        if not super().check_headers(cont_type):
            return False

        uchan_auth = self.headers['Authorization']
        return uchan_auth is not None and 'Basic ' in uchan_auth

    def get_authorization(self):
        """
        Returns the Authorization session key, needed for database querying.
        Please note, this function needs to be called only after check_headers() is called,
        or an AssertionError will be raised.

        :return: OAuth session key from Authorization header, or raise Exception if check_headers() is not called first
        """
        if self.headers is None:
            raise AssertionError('Must call check_headers() first')
        else:
            auth_key = self.headers['Authorization'].replace('Basic ', '', 1)
            sess_key = b64decode(auth_key).decode('utf-8').split(':')

            if sess_key[1] in ['X', 'x']:
                return sess_key[0]
            else:
                return None

    def check_authorization(self):
        """
        Checks for Session table entry related to Authorization header.
        Please note, this function needs to be called only after check_headers() is called,
        or an AssertionError will be raised.

        :return: Session object if Authorization is valid, AssertionError if check_headers() is not called first,
                 AuthException if Authorization is invalid
        """
        if self.headers is None:
            raise AssertionError('Must call check_headers() first')
        else:
            sess_key = self.get_authorization()

            if sess_key is None:
                raise AuthException('Invalid authorization')

            session = Session.query.filter_by(token=sess_key).first()

            if session is None:
                raise AuthException('Invalid authorization')

            return session

    def session_oriented_request(self, func, *args, **kwargs):
        """
        Defines a session oriented request, needed to be implemented into subclasses methods like get(), post() ...
        Subclassess methods must define an inner closure that will be passed to this function.

        Closure has to have and User parameter as first positional argument.
        Other arguments are passed from this method callee.

        :param func:   HTTP method implementation function
        :param args:   Arguments
        :param kwargs: Assigned arguments
        :return:
        """
        try:
            session = self.check_authorization()
            user    = get_user(session.user)

            if user is None:
                return responses.client_error(404, 'User not found')

            return func(user, *args, **kwargs)
        except AuthException as ae:
            return responses.client_error(401, '{}'.format(ae))

    @handler_args
    def media_processing(self):
        """
        Defines a subroutine for media handling in Authorization-driven resources POST methods.
        It checks for argument parsing integrity first (see handler_args decorator), then validate
        file field and goes on with securing filename, decoding image string in binary and write it.

        :return: None
        """
        if not is_valid_file(self.args['image_name']):
            raise ValueError('Image not allowed')

        name, path = new_filename(self.args['image_name'])
        image = decode_file(self.args['image'])

        with open(path, 'wb') as file:
            file.write(image)

        return name


# Module related imports
from server.api import activation, board, hello, me, media
from server.api import post, registration, session, thread, university


__author__  = 'Danilo Cianfrone'
__version__ = 'v3.0'
__doc__     = """Uchan API Resource entities and routings"""
