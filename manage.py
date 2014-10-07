from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Command
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, models

import os

db = SQLAlchemy(app)

migrate = Migrate(app, models.db)
manager = Manager(app)

Translation = Manager(usage="Manage Translations")

pybabel = 'pybabel'

@Translation.command
def update():
    "Updates translation files"
    os.system(pybabel + ' extract -F babel.cfg -k lazy_gettext -o messages.pot app')
    os.system(pybabel + ' update -i messages.pot -d app/translations')
    os.unlink('messages.pot')

@Translation.command
def init(name):
    "initialice a new translation"
    os.system(pybabel + ' extract -F babel.cfg -k lazy_gettext -o messages.pot app')
    os.system(pybabel + ' init -i messages.pot -d app/translations -l ' + name)
    os.unlink('messages.pot')

@Translation.command
def compile():
    "compile translations"
    os.system(pybabel + ' compile -d app/translations')

@manager.command
def ssl():
    from OpenSSL import SSL
    ctx = SSL.Context(SSL.SSLv23_METHOD)
    ctx.use_privatekey_file('ssl.key')
    ctx.use_certificate_file('ssl.cert')
    app.run(ssl_context=ctx)

manager.add_command('db', MigrateCommand)
manager.add_command('tr', Translation)




if __name__ == "__main__":
    manager.run()