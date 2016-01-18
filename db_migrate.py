#!flask/bin/python
import imp
from server import uchan
from config import Config
from migrate.versioning import api

# Database
db = uchan.db


# Restituisce la versione attuale del database
def database_version():
    return api.db_version(Config.SQLALCHEMY_DATABASE_URI,
                          Config.SQLALCHEMY_MIGRATE_REPO)


# Calcola la versione del database
version = database_version()
# Calcola il path della nuova migrazione
migration  = Config.SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (version + 1))
# Crea un modulo per il vecchio modello
tmp_module = imp.new_module('old model')
# Crea il vecchio modello
old_model  = api.create_model(Config.SQLALCHEMY_DATABASE_URI,
                              Config.SQLALCHEMY_MIGRATE_REPO)
# Esegui il vecchio modello
exec(old_model, tmp_module.__dict__)
# Aggiorna il vecchio modello creando un nuovo script
script = api.make_update_script_for_model(Config.SQLALCHEMY_DATABASE_URI,
                                          Config.SQLALCHEMY_MIGRATE_REPO,
                                          tmp_module.meta,
                                          db.metadata)
# Scrivi il nuovo script nella migrazione aggiornata
_file = open(migration, 'wt')
_file.write(script)
_file.close()

# Aggiorna il database
api.upgrade(Config.SQLALCHEMY_DATABASE_URI,
            Config.SQLALCHEMY_MIGRATE_REPO)
# Aggiorna la versione del database
version = database_version()

# Stampa lo stato del modulo
print("New migration saved as " + migration)
print("Current database version: " + str(version))
