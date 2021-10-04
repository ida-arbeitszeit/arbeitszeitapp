from unittest import TestCase

from flask import Flask, _app_ctx_stack, current_app
from flask_sqlalchemy import SQLAlchemy
from injector import Injector, Module, inject, provider, singleton

import project.models
from project import create_app
from project.dependency_injection import configure_injector


class SqliteModule(Module):
    @provider
    @singleton
    def provide_sqlalchemy(self) -> SQLAlchemy:
        db = SQLAlchemy(model_class=project.models.db.Model)
        config = {
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SECRET_KEY": "dev secret key",
            "WTF_CSRF_ENABLED": False,
            "SERVER_NAME": "test.name",
            "ENV": "development",
        }
        app = create_app(config=config, db=db)
        with app.app_context():
            db.create_all()
        app.app_context().push()
        return db

    @provider
    @singleton
    def provide_app(self, _: SQLAlchemy) -> Flask:
        return current_app


class ViewTestCase(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.app = self.injector.get(Flask)
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        _app_ctx_stack.pop()


def get_dependency_injector():
    return Injector([configure_injector, SqliteModule()])


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
