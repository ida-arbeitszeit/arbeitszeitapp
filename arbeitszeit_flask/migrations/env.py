from logging.config import fileConfig
import os

from sqlalchemy import create_engine

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
    if db_uri := os.getenv("ALEMBIC_SQLALCHEMY_DATABASE_URI"):
        return db_uri
    if db_uri := config.get_main_option("sqlalchemy.url"):
        return db_uri
    if db_uri := os.getenv("ARBEITSZEITAPP_DEV_DB"):
        return db_uri
    raise ValueError(
        "No database URI configured. Set ALEMBIC_SQLALCHEMY_DATABASE_URI, "
        "ARBEITSZEITAPP_DEV_DB or sqlalchemy.url in alembic.ini"
    )

def run_migrations_online() -> None:
    connectable = config.attributes.get('connection', None)
    if connectable is None:
        connectable = create_engine(get_db_uri())
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
