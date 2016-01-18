from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

# Import for full deployment
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


class Uchan:
    """
    Uchan wrapping class for api, WSGI app and database.
    Intended for singleton use (even if it's unnecessary).
    """
    app    = Flask(__name__)
    api    = Api(app)
    db     = None
    config = None

    def __init__(self, config: str):
        """
        Construct Uchan class using specified configuration.

        :param config: Configuration class name
        :return: New Uchan object
        """
        self.config = config
        # App configuration
        self.app.config.from_object(self.config)
        self.db = SQLAlchemy(self.app)

    def commit(self):
        """
        Commits changes to app database.

        :return: Nothing
        """
        self.db.session.commit()

    def delete_from_db(self, obj, commit=True):
        """
        Deletes tables from the app database.
        Commits only if necessary.

        :param obj:    Existing database table entry
        :param commit: Specifies if commit is necessary
        :return: Nothing
        """
        self.db.session.delete(obj)
        if commit:
            self.commit()

    def add_to_db(self, obj, commit=True):
        """
        Adds new tables to the app database.
        Commits only if necessary.

        :param obj:    New database table entry
        :param commit: Specifies if commit is necessary
        :return: Nothing
        """
        self.db.session.add(obj)
        if commit:
            self.commit()

    def development_start(self, _port: int):
        """
        Starts Uchan webserver app with Flask-builtin WSGI server engine.
        Intended solely for development and testing phase.

        :param _port: Server port
        :return: Nothing
        """
        self.app.run(host='0.0.0.0', port=_port)

    def deployment_start(self, _port: int):
        """
        Starts Uchan webserver app with Tornado Async WSGI server engine.
        Intended for production phase and full deployment solution.

        :param _port: Server port
        :return: Nothing
        """
        http_server = HTTPServer(WSGIContainer(self.app))
        http_server.listen(_port)
        IOLoop.instance().start()

uchan = Uchan('config.DevelopmentConfig')

from server.api import *
from server.common import *

__author__  = 'Danilo Cianfrone'
__version__ = 'v3.0'
__doc__     = """Flask-based RESTful Server API for uChan platform"""