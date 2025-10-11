from flask import Config as FlaskConfig
from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command
from sqlalchemy import Connection

from arbeitszeit_db.db import Database

def auto_migrate(flask_config: FlaskConfig, db: Database) -> None:
    alembic_config = _get_alembic_config(flask_config)
    if flask_config.get("TESTING", False):
        # Testing: Use the existing connection from the testing session
        _set_connection_to_use_for_migration(alembic_config, db.session.connection())
        alembic_command.ensure_version(alembic_config)
        alembic_command.upgrade(alembic_config, "head")
    else:
        # Dev/Prod: Create a new connection
        with db.engine.begin() as connection:
            _set_connection_to_use_for_migration(alembic_config, connection)
            alembic_command.ensure_version(alembic_config)
            alembic_command.upgrade(alembic_config, "head")

def _get_alembic_config(flask_config: FlaskConfig) -> AlembicConfig:
    return AlembicConfig(flask_config["ALEMBIC_CONFIGURATION_FILE"])

def _set_connection_to_use_for_migration(alembic_config: AlembicConfig, connection: Connection) -> None:
    # For details see:
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#sharing-a-connection-across-one-or-more-programmatic-migration-commands
    alembic_config.attributes["connection"] = connection
