from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from flask import Flask
from sqlalchemy import inspect, text

from arbeitszeit.injector import Binder, CallableProvider, Module
from arbeitszeit_db.db import Base
from tests.flask_integration.flask import DatabaseTestCase

from .dependency_injection import FlaskConfiguration


class MigrationsTestCase(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        Base.metadata.drop_all(bind=self.db.engine)
        with self.db.engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version;"))
        self.alembic_config = Config("tests/flask_integration/alembic.ini")

    def tearDown(self) -> None:
        Base.metadata.drop_all(bind=self.db.engine)
        Base.metadata.create_all(bind=self.db.engine)
        super().tearDown()

    @property
    def auto_migrate_setting(self) -> bool:
        raise NotImplementedError()

    def get_injection_modules(self) -> list[Module]:
        auto_migrate_setting = self.auto_migrate_setting

        class _Module(Module):
            def configure(self, binder: Binder) -> None:
                super().configure(binder)
                binder[FlaskConfiguration] = CallableProvider(
                    _Module.provide_flask_configuration
                )

            @staticmethod
            def provide_flask_configuration() -> FlaskConfiguration:
                configuration = FlaskConfiguration.default()
                configuration["AUTO_MIGRATE"] = auto_migrate_setting
                return configuration

        modules = super().get_injection_modules()
        modules.append(_Module())
        return modules

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
        current_version_row = self.db.session.execute(
            text("select version_num from alembic_version;")
        ).first()
        assert current_version_row
        assert current_version_row[0] == VERSION

    def is_db_at_head(self) -> bool:
        current_version_row = self.db.session.execute(
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
    @property
    def auto_migrate_setting(self) -> bool:
        return True

    def test_that_app_starts_successfully(self) -> None:
        self.injector.get(Flask)

    def test_that_tables_are_created(self) -> None:
        assert not self.table_exists("alembic_version")
        assert not self.table_exists("plan")
        self.injector.get(Flask)
        assert self.table_exists("alembic_version")
        assert self.table_exists("plan")


class TestsWithFreshDatabaseAndNoAutoMigration(MigrationsTestCase):
    @property
    def auto_migrate_setting(self) -> bool:
        return False

    def test_that_app_starts_successfully(self) -> None:
        self.injector.get(Flask)

    def test_that_tables_are_created(self) -> None:
        assert not self.table_exists("alembic_version")
        assert not self.table_exists("plan")
        self.injector.get(Flask)
        assert self.table_exists("alembic_version")
        assert self.table_exists("plan")

    def test_that_alembic_table_has_version_num(self) -> None:
        self.injector.get(Flask)
        version_row = self.db.session.execute(
            text("select version_num from alembic_version;")
        ).first()
        assert version_row
        assert version_row[0]


class TestsWithUpgradableDatabaseAndAutoMigration(MigrationsTestCase):
    @property
    def auto_migrate_setting(self) -> bool:
        return True

    def setUp(self) -> None:
        super().setUp()
        self.bring_database_to_upgradable_version()

    def test_that_app_starts_successfully(self) -> None:
        self.injector.get(Flask)

    def test_that_db_gets_upgraded_to_head(self) -> None:
        assert not self.is_db_at_head()
        self.injector.get(Flask)
        assert self.is_db_at_head()


class TestsWithUpgradableDatabaseAndNoAutoMigration(MigrationsTestCase):
    @property
    def auto_migrate_setting(self) -> bool:
        return False

    def setUp(self) -> None:
        super().setUp()
        self.bring_database_to_upgradable_version()

    def test_that_app_starts_successfully(self) -> None:
        self.injector.get(Flask)

    def test_that_db_does_not_get_upgraded_to_head(self) -> None:
        self.injector.get(Flask)
        assert not self.is_db_at_head()


class TestDowngrade(MigrationsTestCase):
    @property
    def auto_migrate_setting(self) -> bool:
        return False

    def test_that_downgrade_to_base_is_possible_after_an_upgrade_to_head(self) -> None:
        with self.db.engine.begin() as connection:
            self.alembic_config.attributes["connection"] = connection
            command.upgrade(self.alembic_config, "head")
            command.downgrade(self.alembic_config, "base")
