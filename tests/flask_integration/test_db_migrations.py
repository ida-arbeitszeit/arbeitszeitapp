from flask import Flask
from sqlalchemy import inspect

from arbeitszeit.injector import Binder, CallableProvider, Module
from tests.flask_integration.flask import DatabaseTestCase, drop_and_recreate_schema

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
        drop_and_recreate_schema(self.connection)

    def test_that_app_starts_successfully_when_auto_migrate_is_enabled(self) -> None:
        self.injector.get(Flask)

    def test_that_tables_are_created_when_auto_migrate_is_enabled(self) -> None:
        assert not self.table_exists("alembic_version")
        assert not self.table_exists("plan")
        self.injector.get(Flask)
        assert self.table_exists("alembic_version")
        assert self.table_exists("plan")

    def table_exists(self, table_name: str) -> bool:
        inspector = inspect(self.db.session.connection())
        tables = inspector.get_table_names()
        return table_name in tables
