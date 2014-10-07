from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, models
db = SQLAlchemy(app)

migrate = Migrate(app, models.db)
manager = Manager(app)

@manager.command
def ssl():
    from OpenSSL import SSL
    ctx = SSL.Context(SSL.SSLv23_METHOD)
    ctx.use_privatekey_file('ssl.key')
    ctx.use_certificate_file('ssl.cert')
    app.run(ssl_context=ctx)

manager.add_command('db', MigrateCommand)




if __name__ == "__main__":
    manager.run()