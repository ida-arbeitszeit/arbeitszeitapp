from flask import Config
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import Engine

def migrate(flask_config: Config, engine: Engine) -> None:
    # For details see:
    # https://alembic.sqlalchemy.org/en/latest/cookbook.html#sharing-a-connection-across-one-or-more-programmatic-migration-commands
    alembic_cfg = AlembicConfig(flask_config["ALEMBIC_CONFIGURATION_FILE"])
    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        alembic_command.ensure_version(alembic_cfg)
        alembic_command.upgrade(alembic_cfg, "head")
