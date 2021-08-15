from flask_sqlalchemy import SQLAlchemy
from injector import Injector, Module, inject, provider, singleton

import project.models
from project import create_app
from project.database import configure_injector


class SqliteModule(Module):
    @provider
    @singleton
    def provide_sqlalchemy(self) -> SQLAlchemy:
        db = SQLAlchemy(model_class=project.models.db.Model)
        config = {
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
        app = create_app(config=config, db=db)
        with app.app_context():
            db.create_all()
        app.app_context().push()
        return db


def injection_test(original_test):
    injector = Injector([configure_injector, SqliteModule()])

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
