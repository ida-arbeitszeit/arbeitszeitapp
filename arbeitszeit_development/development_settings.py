"""
The settings in this module override settings in configuration_base.py.
"""

from os import environ

from arbeitszeit_flask.mail_service.debug_mail_service import DebugMailService

PREFERRED_URL_SCHEME = "http"
TESTING = True

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
REMEMBER_COOKIE_HTTPONLY = True

# mail
MAIL_SERVER = environ.get("MAIL_SERVER", "localhost")
MAIL_PORT = environ.get("MAIL_PORT", "0")
MAIL_USERNAME = environ.get("MAIL_USERNAME", "")
MAIL_PASSWORD = environ.get("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER = environ.get("MAIL_DEFAULT_SENDER", "admin@dev.org")
MAIL_ADMIN = environ.get("MAIL_ADMIN", "admin@dev.org")
MAIL_USE_TLS = False
MAIL_USE_SSL = True

FLASK_PROFILER = {
    "enabled": True,
    "endpointRoot": "profiling",
}

SECRET_KEY = environ.get("DEV_SECRET_KEY", "dev secret key")
SQLALCHEMY_DATABASE_URI = environ["ARBEITSZEITAPP_DEV_DB"]
SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT", "dev password salt")
SERVER_NAME = environ.get("ARBEITSZEITAPP_SERVER_NAME", "127.0.0.1:5000")
DEFAULT_USER_TIMEZONE = environ.get("DEFAULT_USER_TIMEZONE", "UTC")
ALLOWED_OVERDRAW_MEMBER = environ.get("ALLOWED_OVERDRAW_MEMBER", "unlimited")
ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION = environ.get(
    "ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION", "33"
)
MAIL_PLUGIN_MODULE = DebugMailService.__module__
MAIL_PLUGIN_CLASS = DebugMailService.__name__
