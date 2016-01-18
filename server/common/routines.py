import re
from os import urandom
from hashlib import sha256
from binascii import b2a_hex
from base64 import b64encode
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

# API related imports
from server.models import User