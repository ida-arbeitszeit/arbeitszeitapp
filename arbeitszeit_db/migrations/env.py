import logging
import os
from logging.config import fileConfig

from alembic import context
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, create_engine, inspect

from arbeitszeit_db.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic")


target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def is_fresh_db(connection: Connection) -> bool:
    inspector = inspect(connection)
    return "alembic_version" not in inspector.get_table_names()


def init_db(migration_context: MigrationContext) -> None:
    """Create all tables and stamp as newest version."""
    bind = migration_context.bind
    assert bind
    engine = bind.engine
    Base.metadata.create_all(engine)
    migration_context.stamp(
        script_directory=ScriptDirectory.from_config(config), revision="head"
    )


def upgrade_to_head_if_database_is_fresh(connection: Connection) -> None:
    migration_context = context.get_context()
    if is_fresh_db(connection):
        logger.info(
            "Fresh database detected, creating all tables and stamping to head."
        )
        init_db(migration_context)


def get_db_uri() -> str:
    if db_uri := os.getenv("ALEMBIC_SQLALCHEMY_DATABASE_URI"):
        return db_uri
    if db_uri := config.get_main_option("sqlalchemy.url"):
        return db_uri
    raise ValueError(
        "No database URI configured. Set ALEMBIC_SQLALCHEMY_DATABASE_URI "
        "or sqlalchemy.url in alembic.ini"
    )


def run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    upgrade_to_head_if_database_is_fresh(connection)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = config.attributes.get("connection", None)
    if connectable:
        run_migrations(connectable)
    else:
        engine = create_engine(get_db_uri())
        with engine.connect() as connection:
            run_migrations(connection)


if context.is_offline_mode():
    raise NotImplementedError()
else:
    run_migrations_online()
