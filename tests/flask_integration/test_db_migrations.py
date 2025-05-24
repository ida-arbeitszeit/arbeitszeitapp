from flask import Flask
from sqlalchemy import inspect

from arbeitszeit.injector import Binder, CallableProvider, Module
from arbeitszeit_flask.database.db import Base
from tests.flask_integration.flask import DatabaseTestCase

from .dependency_injection import FlaskConfiguration


class AutoMigrationsTestCase(DatabaseTestCase):
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


class AutoMigrationTests(AutoMigrationsTestCase):
    @property
    def auto_migrate_setting(self) -> bool:
        return True

    def setUp(self) -> None:
        super().setUp()
        Base.metadata.drop_all(self.db.engine)

    def test_that_app_starts_successfully_when_auto_migrate_is_enabled(self) -> None:
        self.injector.get(Flask)

    def test_that_tables_are_created_when_auto_migrate_is_enabled(self) -> None:
        self.assertTableNotExists("alembic_version")
        self.assertTableNotExists("plan")
        self.injector.get(Flask)
        self.assertTableExists("alembic_version")
        self.assertTableExists("plan")

    def assertTableNotExists(self, table_name: str) -> None:
        inspector = inspect(self.db.session.connection())
        tables = inspector.get_table_names()
        assert table_name not in tables

    def assertTableExists(self, table_name: str) -> None:
        inspector = inspect(self.db.session.connection())
        tables = inspector.get_table_names()
        assert table_name in tables
