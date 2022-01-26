from typing import List, Optional

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from injector import Injector, Module, inject, provider, singleton

from project import create_app
from project.dependency_injection import FlaskModule
from project.extensions import db


class FlaskConfiguration(dict):
    def _get_template_folder(self) -> Optional[str]:
        return self.get("template_folder")

    def _set_template_folder(self, template_folder: Optional[str]) -> None:
        self["template_folder"] = template_folder

    # Allows you to control where flask loads templates from.
    template_folder = property(_get_template_folder, _set_template_folder)


FLASK_TESTING_CONFIGURATION = FlaskConfiguration(
    {
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "dev secret key",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "test.name",
        "ENV": "development",
        "DEBUG_DETAILS": False,
        "SECURITY_PASSWORD_SALT": "dev password salt",
        "TESTING": True,
        "MAIL_DEFAULT_SENDER": "test_sender@cp.org",
        "MAIL_BACKEND": "flask_mail",
        "LANGUAGES": {"en": "English", "de": "Deutsch"},
    }
)


class SqliteModule(Module):
    @provider
    @singleton
    def provide_sqlalchemy(self, config: FlaskConfiguration) -> SQLAlchemy:
        _db = db
        app = create_app(config=config, db=_db, template_folder=config.template_folder)
        with app.app_context():
            _db.create_all()
        app.app_context().push()
        return _db

    @provider
    @singleton
    def provide_app(self, _: SQLAlchemy) -> Flask:
        return current_app

    @provider
    def provide_flask_configuration(self) -> FlaskConfiguration:
        return FLASK_TESTING_CONFIGURATION


def get_dependency_injector(additional_modules: Optional[List[Module]] = None):
    modules: List[Module] = [FlaskModule(), SqliteModule()]
    if additional_modules is not None:
        modules.extend(additional_modules)
    return Injector(modules)


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
