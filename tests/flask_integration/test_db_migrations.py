from arbeitszeit.injector import Binder, CallableProvider, Module
from tests.flask_integration.flask import FlaskTestCase

from .dependency_injection import FlaskConfiguration


class AutoMigrationsTestCase(FlaskTestCase):
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

    def test_that_app_starts_successfully_with_auto_migrate(self) -> None:
        assert self.app
