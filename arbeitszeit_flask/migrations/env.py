from logging.config import fileConfig

from arbeitszeit_flask import load_configuration

from arbeitszeit_flask.database.db import Database
from flask import Flask

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 'autogenerate' support
from arbeitszeit_flask.database.models import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    raise NotImplementedError()

def get_db_uri() -> str:
    tmp_flask_app = Flask(__name__)
    load_configuration(tmp_flask_app)
    db_uri = tmp_flask_app.config["SQLALCHEMY_DATABASE_URI"]
    return db_uri

def run_migrations_online() -> None:
    connectable = config.attributes.get('connection', None)
    if connectable is None:
        Database().configure(get_db_uri())   
        connectable = Database().engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )

            with context.begin_transaction():
                context.run_migrations()
    else:
        context.configure(
            connection=connectable,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
