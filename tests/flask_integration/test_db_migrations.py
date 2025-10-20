from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

from arbeitszeit_db.db import Base
from arbeitszeit_flask import create_app
from tests.db.base_test_case import TestCaseWithResettedDatabase

from .dependency_injection import FlaskConfiguration


class MigrationsTestCase(TestCaseWithResettedDatabase):
    """
    Migration tests need to perform actual DDL operations (CREATE TABLE, etc.)
    so they cannot use the transaction rollback pattern. Instead, they clean up
    by dropping all tables after each test.
    """

    def setUp(self) -> None:
        super().setUp()
        Base.metadata.drop_all(bind=self.db.engine)
        with self.db.engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))

        self.alembic_config = Config("tests/flask_integration/alembic.ini")
        self.flask_config = FlaskConfiguration.default()

    def tearDown(self) -> None:
        with self.db.engine.begin() as conn:
            Base.metadata.drop_all(bind=conn)
            conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
        super().tearDown()

    def table_exists(self, table_name: str) -> bool:
        inspector = inspect(self.db.engine)
        tables = inspector.get_table_names()
        return table_name in tables

    def bring_database_to_upgradable_version(self) -> None:
        VERSION = "480a749375de"
        with self.db.engine.begin() as connection:
            self.alembic_config.attributes["connection"] = connection
            command.upgrade(self.alembic_config, "head")
            command.downgrade(self.alembic_config, VERSION)

        # Query the version using the regular session
        with self.db.engine.connect() as conn:
            current_version_row = conn.execute(
                text("select version_num from alembic_version;")
            ).first()
            assert current_version_row
            assert current_version_row[0] == VERSION

    def is_db_at_head(self) -> bool:
        with self.db.engine.connect() as conn:
            current_version_row = conn.execute(
                text("select version_num from alembic_version;")
            ).first()
            if not current_version_row:
                return False
            current_version = current_version_row[0]

        # Get the head revision from alembic metadata
        script_directory = ScriptDirectory.from_config(self.alembic_config)
        head_revisions = script_directory.get_heads()
        return current_version in head_revisions


class TestsWithFreshDatabaseAndAutoMigration(MigrationsTestCase):
    def setUp(self):
        super().setUp()
        self.flask_config["AUTO_MIGRATE"] = True

    def test_that_app_starts_successfully(self) -> None:
        create_app(self.flask_config)

    def test_that_tables_are_created(self) -> None:
        assert not self.table_exists("alembic_version")
        assert not self.table_exists("plan")
        create_app(self.flask_config)
        assert self.table_exists("alembic_version")
        assert self.table_exists("plan")


class TestsWithFreshDatabaseAndNoAutoMigration(MigrationsTestCase):
    def setUp(self):
        super().setUp()
        self.flask_config["AUTO_MIGRATE"] = False

    def test_that_app_starts_successfully(self) -> None:
        create_app(self.flask_config)

    def test_that_tables_are_created(self) -> None:
        assert not self.table_exists("alembic_version")
        assert not self.table_exists("plan")
        create_app(self.flask_config)
        assert self.table_exists("alembic_version")
        assert self.table_exists("plan")

    def test_that_alembic_table_has_version_num(self) -> None:
        create_app(self.flask_config)
        with self.db.engine.connect() as conn:
            version_row = conn.execute(
                text("select version_num from alembic_version;")
            ).first()
        assert version_row
        assert version_row[0]


class TestsWithUpgradableDatabaseAndAutoMigration(MigrationsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.flask_config["AUTO_MIGRATE"] = True
        self.bring_database_to_upgradable_version()

    def test_that_app_starts_successfully(self) -> None:
        create_app(self.flask_config)

    def test_that_db_gets_upgraded_to_head(self) -> None:
        assert not self.is_db_at_head()
        create_app(self.flask_config)
        assert self.is_db_at_head()


class TestsWithUpgradableDatabaseAndNoAutoMigration(MigrationsTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.flask_config["AUTO_MIGRATE"] = False
        self.bring_database_to_upgradable_version()

    def test_that_app_starts_successfully(self) -> None:
        create_app(self.flask_config)

    def test_that_db_does_not_get_upgraded_to_head(self) -> None:
        create_app(self.flask_config)
        assert not self.is_db_at_head()


class TestDowngrade(MigrationsTestCase):
    def test_that_downgrade_to_base_is_possible_after_an_upgrade_to_head(self) -> None:
        with self.db.engine.begin() as connection:
            self.alembic_config.attributes["connection"] = connection
            command.upgrade(self.alembic_config, "head")
            command.downgrade(self.alembic_config, "base")
