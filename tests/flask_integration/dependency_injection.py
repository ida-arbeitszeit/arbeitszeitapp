from __future__ import annotations

import os
from typing import List, Optional

from flask import Flask

from arbeitszeit.injector import Binder, CallableProvider, Injector, Module
from arbeitszeit_flask import create_app
from arbeitszeit_flask.database.db import Database
from arbeitszeit_flask.dependency_injection import FlaskModule
from tests.dependency_injection import TestingModule
from tests.flask_integration.mail_service import MockEmailService


class FlaskConfiguration(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if key.isupper():
                setattr(self, key, value)

    @classmethod
    def default(cls) -> FlaskConfiguration:
        return cls(
            {
                "SQLALCHEMY_DATABASE_URI": provide_test_database_uri(),
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SECRET_KEY": "dev secret key",
                "WTF_CSRF_ENABLED": False,
                "SERVER_NAME": "test.name",
                "DEBUG": True,
                "DEBUG_DETAILS": False,
                "SECURITY_PASSWORD_SALT": "dev password salt",
                "TESTING": True,
                "MAIL_DEFAULT_SENDER": "test_sender@cp.org",
                "MAIL_ADMIN": "test_admin@cp.org",
                "MAIL_PLUGIN_MODULE": MockEmailService.__module__,
                "MAIL_PLUGIN_CLASS": MockEmailService.__name__,
                "LANGUAGES": {"en": "English", "de": "Deutsch", "es": "Español"},
                "ARBEITSZEIT_PASSWORD_HASHER": "tests.password_hasher:PasswordHasherImpl",
                "AUTO_MIGRATE": False,
            }
        )

    def _get_template_folder(self) -> Optional[str]:
        return self.get("template_folder")

    def _set_template_folder(self, template_folder: Optional[str]) -> None:
        self["template_folder"] = template_folder

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key.isupper():
            setattr(self, key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
        if key.isupper():
            delattr(self, key)

    # Allows you to control where flask loads templates from.
    template_folder = property(_get_template_folder, _set_template_folder)


def provide_test_database_uri() -> str:
    uri = os.getenv("ARBEITSZEITAPP_TEST_DB")
    if uri is None:
        raise ValueError(
            "Environment variable ARBEITSZEITAPP_TEST_DB is unset. Set it to point to a postgres db"
        )
    return uri


def provide_app(config: FlaskConfiguration) -> Flask:
    return create_app(config=config, template_folder=config.template_folder)


def provide_database() -> Database:
    Database().configure(uri=provide_test_database_uri())
    return Database()


class DatabaseModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Flask] = CallableProvider(provide_app, is_singleton=True)
        binder[FlaskConfiguration] = CallableProvider(FlaskConfiguration.default)
        binder[Database] = CallableProvider(provide_database, is_singleton=True)


def get_dependency_injector(
    additional_modules: Optional[List[Module]] = None,
) -> Injector:
    # Please be aware that the get_dependency_injector function is only called
    # from the testing side. The app itself is used with its default dependency
    # injector. Influencing the dependency injector used by the app is
    # currently only possible via configuration options.
    modules: List[Module] = [
        FlaskModule(),
        TestingModule(),
        DatabaseModule(),
    ]
    if additional_modules is not None:
        modules.extend(additional_modules)
    return Injector(modules)
