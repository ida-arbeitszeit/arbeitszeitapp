"""These functions are intended to be used during Flask app initialization."""

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from alembic.migration import MigrationContext
from flask import Config as FlaskConfig
from sqlalchemy import Engine

from arbeitszeit_db.db import Base, Database


def auto_migrate(flask_config: FlaskConfig, db: Database) -> None:
    alembic_config = AlembicConfig(flask_config["ALEMBIC_CONFIGURATION_FILE"])
    with db.engine.begin() as connection:
        alembic_config.attributes["connection"] = connection
        initialize_or_update_database(db.engine, alembic_config)


def initialize_or_update_database(engine: Engine, alembic_config: AlembicConfig):
    """
    Initialize a new database or update an existing one.
    If the database is new (no alembic_version table or no applied revisions),
    create all tables and stamp the database with the latest revision.
    If the database already exists, apply all pending migrations to bring it up to date.
    """
    if is_new_database(engine):
        Base.metadata.create_all(engine)
        alembic_command.stamp(alembic_config, "head")
    else:
        alembic_command.upgrade(alembic_config, "head")


def is_new_database(engine: Engine) -> bool:
    """No version table or no revisions applied yet means new database."""
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_heads = context.get_current_heads()
        if not current_heads:
            return True
    return False
