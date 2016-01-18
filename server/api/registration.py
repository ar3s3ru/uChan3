from os import urandom
from hashlib import md5
from binascii import b2a_hex
# Flask related imports
from sqlalchemy.exc import IntegrityError
# API related imports
from server import uchan
from server.api import BasicEntity
from server.api import handler_data, handler_args
from server.common import responses, routines
# DB Models related imports
from server.models import User


class Registration(BasicEntity):
    """
    API Registration resource.
    Subclassed from BasicEntity, which means there are no OAuth lookups for this API routing.

    It only uses POST method, with JSON arguments included in __init__ constructor.
    """

    def __init__(self):
        """
        Construct the Registration resource entity.

        Calls the BasicEntity superclass for headers parsing, and adds the desired request body parsing
        for POST method.

        :return: Registration resource object
        """
        super().__init__()

        self.form.add_argument('nickname', type=str, location='json')
        self.form.add_argument('password', type=str, location='json')
        self.form.add_argument('gender', type=str, location='json')
        self.form.add_argument('university', type=int, location='json')
        self.form.add_argument('deviceId', type=str, location='json')
        self.form.add_argument('email', type=str, location='json')

    @handler_args
    def validate_args(self):
        """
        Check if all required arguments are valid.

        :return: Raises ValueError if some required arguments are invalid, else nothing
        """
        if not routines.is_valid_nick(self.args['nickname']):
            raise ValueError('Invalid parameter: nickname')
        elif not routines.is_valid_pass(self.args['password']):
            raise ValueError('Invalid parameter: password')
        elif not routines.is_valid_email(self.args['email']):
            raise ValueError('Invalid parameter: email')
        elif self.args['university'] < 2 or self.args['university'] > 68:
            raise ValueError('Invalid parameter: university')
        elif not self.args['gender'] in ['m', 'M', 'f', 'F']:
            raise ValueError('Invalid parameter: gender')

    @handler_args
    def check_existing_email(self):
        """
        Check if there are not existing emails conflicting with email specified.

        :return: If email specified in request body is not already registered
        """
        return User.query.filter_by(email=self.args['email'],
                                    university=self.args['university']).first() is None

    @handler_args
    def check_existing_nickname(self):
        """
        Check if there are not existing nicknames conflicting with nickname specified.

        :return: If nickname specified in request body is not already registered
        """
        return User.query.filter_by(nickname=self.args['nickname']).first() is None

    @staticmethod
    def generate_salt():
        """
        Generate salt for salted hashing password storage.

        :return: Salt for password storage
        """
        return str(b2a_hex(urandom(10)))[2:22]

    @handler_args
    def generate_token(self):
        """
        Generate activation token.

        :return: Activation token for user just registered
        """
        secret_key = uchan.app.config.get('SECRET_KEY')
        hashing    = str.encode(self.args['nickname'] + self.args['deviceId'] + secret_key)
        hashed     = md5(hashing).hexdigest()

        p1 = hashed[0:7]
        p2 = hashed[7:11]
        p3 = hashed[11:15]
        p4 = hashed[15:19]
        p5 = hashed[19:]

        return p1 + '-' + p2 + '-' + p3 + '-' + p4 + '-' + p5

    @handler_data
    def post(self):
        """
        POST method implementation for API Registration resource entity.

        :return: JSON response to Registration method (201 Created, 409 Conflict, 400 Bad Request)
        """
        try:
            # Arguments validation
            self.check_args()
            self.validate_args()

            # Integrity checks
            if not self.check_existing_email():
                return responses.client_error(409, 'Email already registered')

            if not self.check_existing_nickname():
                return responses.client_error(409, 'Nickname already registered')

            salt, token = self.generate_salt(), self.generate_token()

            # Creating new User entity
            user = User(self.args['nickname'], routines.hashing_password(salt, self.args['password']), salt,
                        self.args['university'], self.args['email'], self.args['gender'], False, token)

            # TODO: remove this and insert email sending
            print(user.token)

            # Add new entity to database
            uchan.add_to_db(user)
            return responses.successful(201, 'Registration sent')
        except ValueError as msg:
            # Arguments validation error
            return responses.client_error(400, '{}'.format(msg))
        except IntegrityError as msg:
            # Database integrity error
            return responses.client_error(409, 'Registration error, check your JSON or contact server manteiner'
                                          .format(msg))

# Add resource to API routing
uchan.api.add_resource(Registration, '/api/registration')
