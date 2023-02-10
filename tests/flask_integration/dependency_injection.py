from __future__ import annotations

from typing import List, Optional

from flask import Flask

from arbeitszeit.injector import Binder, CallableProvider, Injector, Module
from arbeitszeit_flask import create_app
from arbeitszeit_flask.dependency_injection import FlaskModule
from arbeitszeit_flask.extensions import db
from tests.dependency_injection import TestingModule


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
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "SECRET_KEY": "dev secret key",
                "WTF_CSRF_ENABLED": False,
                "SERVER_NAME": "test.name",
                "DEBUG": True,
                "DEBUG_DETAILS": False,
                "SECURITY_PASSWORD_SALT": "dev password salt",
                "TESTING": True,
                "MAIL_DEFAULT_SENDER": "test_sender@cp.org",
                "MAIL_BACKEND": "flask_mail",
                "LANGUAGES": {"en": "English", "de": "Deutsch"},
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


def provide_app(config: FlaskConfiguration) -> Flask:
    return create_app(config=config, db=db, template_folder=config.template_folder)


class SqliteModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Flask] = CallableProvider(provide_app, is_singleton=True)
        binder[FlaskConfiguration] = CallableProvider(FlaskConfiguration.default)


def get_dependency_injector(additional_modules: Optional[List[Module]] = None):
    modules: List[Module] = [
        FlaskModule(),
        TestingModule(),
        SqliteModule(),
    ]
    if additional_modules is not None:
        modules.extend(additional_modules)
    return Injector(modules)
