import os.path

basedir    = os.path.abspath(os.path.dirname(__file__)) + '/server/database'
staticdir  = os.path.abspath(os.path.dirname(__file__)) + '/server/static'


class Config:
    """
    Flask-RESTful configuration class.
    All configuration fields will be added here.

    To use a particular configuration, subclass from this.
    """
    DEBUG   = False
    TESTING = False

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'server.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'repository')

    SECRET_KEY = 'Insert Secret Key'

    UPLOAD_FOLDER = staticdir
    ALLOWED_EXTENSIONS = {'png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG', 'gif', 'GIF'}
    MAX_CONTENT_LENGHT = 4 * 1024 * 1024  # 4MB lenght upper bound


class DevelopmentConfig(Config):
    """
    Subclassed from Config, serves for development stage.
    """
    DEBUG = True


class TestingConfig(Config):
    """
    Subclassed from Config, serves for testing stage.
    """
    TESTING = True
