import re
from uuid import uuid4
from os import urandom, path
from hashlib import sha256
from binascii import b2a_hex
from base64 import b64encode, b64decode
from crcmod.predefined import Crc


def calculate_authid(tid: int, uid: int):
    """
    Calculate anonymous authID from nickname and thread id.

    :param uid: Anonymous User ID
    :param tid: Thread ID
    :return: Anonymous authID
    """
    rand  = str(b2a_hex(urandom(4)))[2:10]
    crc16 = Crc('crc-16')
    crc16.update((str(uid) + ":" + str(tid) + rand).encode('utf-8'))
    return b64encode(crc16.hexdigest().encode('utf-8')).decode('utf-8')


def hashing_password(salt: str, password: str):
    """
    Generate hash password for database storage.

    :param salt:     User salt
    :param password: User password
    :return: Salt hashed user password
    """
    return sha256(str.encode(salt + password)).hexdigest()


def decode_file(file: str):
    """
    Decode file represented in Base64 to its original form.

    :param file: Base64 file representation
    :return: Original binary format file
    """
    return b64decode(file)


def new_filepath(image_name: str):
    """
    Returns the new file uploaded path.

    :param image_name: New uploaded image name
    :return: New uploaded image path
    """
    return path.join(uchan.app.config.get('UPLOAD_FOLDER'), image_name)


def new_filename(image_name: str):
    """
    Returns the new file uploaded name.

    :param image_name: Old file uploaded name
    :return: New file uploaded name and new file path
    """
    while True:
        new_name = str(uuid4()) + '.' + image_name.rsplit('.', 1)[1]
        new_path = new_filepath(new_name)

        if not path.exists(new_path):
            return new_name, new_path


def str_to_bool(val: str):
    """
    Converts boolean string value in boolean.

    :param val: Boolean string value
    :return: Boolean value
    """
    str_val = {'True': True, 'true': True, 'False': False, 'false': False}
    return str_val[val]


###############################################################################
# Regular Expression checks support                                           #
###############################################################################
RENickname = re.compile(r'^(?=.*?[a-z])[A-Za-z\d_.]{5,20}$')
REPassword = re.compile(r'^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{5,30}$')
REEmail    = re.compile(r'[A-Za-z\d_.]{1,20}')


def is_valid_nick(nick: str):
    """
    Checks nickname user input.
    Nicknames can have any type of alphanumerical characters, underscore and points,
    and lenght between 5 and 20 characters.

    :param nick: Nickname user input
    :return: If nickname is valid or not
    """
    res = RENickname.match(nick)
    return not (res is None or len(res.string) < len(nick))


def is_valid_pass(passw: str):
    """
    Checks password user input.
    Password must have at least one capital letter, one number and lenght between 5 and 30 characters.

    :param passw: Password user input
    :return: If password is valid or not
    """
    res = REPassword.match(passw)
    return not (res is None or len(res.string) < len(passw))


def is_valid_email(name: str):
    """
    Checks email user input
    Email must be from 1 to 20 characters long.

    :param name: Email user input
    :return: If email is valid or not
    """
    res = REEmail.match(name)
    return not (res is None or len(res.string) < len(name))


def is_valid_file(image_name: str):
    """
    Check if file submitted name is a valid name.

    :param image_name: Image submitted name
    :return: If image name is valid
    """
    return '.' in image_name and image_name.rsplit('.', 1)[1] in uchan.app.config.get('ALLOWED_EXTENSIONS')


###############################################################################
# Database functions                                                          #
###############################################################################
def get_user(user_id: int):
    """
    Returns User object from user_id foreign key.

    :param user_id: User ID foreign key
    :return: User object related
    """
    return User.query.get(user_id)


def get_request(thread, user):
    """
    Get request URL from Thread and User author object.

    :param thread: Thread object
    :param user:   User requested object
    :return: Request URL (from endpoint) if exists, else None
    """
    if thread is None:
        raise ValueError('Invalid parameter: thread')

    if user is None:
        raise ValueError('Invalid parameter: user')

    threaduser = thread.get_threaduser(user.id)

    return 'chat/request/' + threaduser.id if threaduser is not None else None

# API related imports
from server import uchan
from server.models import User
