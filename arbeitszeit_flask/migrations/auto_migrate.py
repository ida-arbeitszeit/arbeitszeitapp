from flask import Config
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

from arbeitszeit_flask.database.db import Database

def auto_migrate(flask_config: Config, db: Database) -> None:
    # For details see:
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#sharing-a-connection-across-one-or-more-programmatic-migration-commands
    alembic_cfg = AlembicConfig(flask_config["ALEMBIC_CONFIGURATION_FILE"])

    if flask_config.get("TESTING", False):
        # Use the connection from the testing session
        alembic_cfg.attributes["connection"] = db.session.connection()
        alembic_command.ensure_version(alembic_cfg)
        alembic_command.upgrade(alembic_cfg, "head")
    else:
        # Use a new connection, commiting it to the database
        with db.engine.begin() as connection:
            alembic_cfg.attributes["connection"] = connection
            alembic_command.ensure_version(alembic_cfg)
            alembic_command.upgrade(alembic_cfg, "head")
