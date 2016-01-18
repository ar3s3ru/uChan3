#!flask/bin/python
import os.path
from server import uchan
from config import Config
from migrate.versioning import api

# Crea il database
uchan.db.create_all()

if not os.path.exists(Config.SQLALCHEMY_MIGRATE_REPO):
    api.create(Config.SQLALCHEMY_MIGRATE_REPO, 'Database Repository')
    api.version_control(Config.SQLALCHEMY_DATABASE_URI,
                        Config.SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(Config.SQLALCHEMY_DATABASE_URI,
                        Config.SQLALCHEMY_MIGRATE_REPO,
                        api.version(Config.SQLALCHEMY_MIGRATE_REPO))