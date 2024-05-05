import importlib

from flask import Flask, current_app

from .debug_mail_service import DebugMailService
from .flask_mail import FlaskMailService
from .interface import EmailPlugin


def load_email_plugin(app: Flask) -> None:
    # This is an exception to the usual email plugin configuration and *should*
    # be deleted as soon as we don't use flask_mail anymore. Any other email
    # plugins must be configured using the MAIL_PLUGIN_MODULE and
    # MAIL_PLUGIN_CLASS variables.
    if app.config.get("MAIL_BACKEND") == "flask_mail":
        module_name = FlaskMailService.__module__
        class_name = FlaskMailService.__name__
    else:
        module_name = app.config.get("MAIL_PLUGIN_MODULE", DebugMailService.__module__)
        class_name = app.config.get("MAIL_PLUGIN_CLASS", DebugMailService.__name__)
    module = importlib.import_module(module_name)
    plugin_class = getattr(module, class_name)
    assert issubclass(plugin_class, EmailPlugin)
    app.extensions["arbeitszeit_email_plugin"] = plugin_class.initialize_plugin(app)


def get_mail_service() -> EmailPlugin:
    return current_app.extensions["arbeitszeit_email_plugin"]
