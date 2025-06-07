from os import environ

PREFERRED_URL_SCHEME = "http"
DEBUG_DETAILS = environ.get("DEBUG_DETAILS") in ("true", "True", "1", "t")
TESTING = True
SQLALCHEMY_DATABASE_URI = environ.get("DEV_DATABASE_URI")
SECRET_KEY = environ.get("DEV_SECRET_KEY")
SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT")

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
REMEMBER_COOKIE_HTTPONLY = True
SERVER_NAME = environ.get("ARBEITSZEIT_APP_SERVER_NAME")

# mail
MAIL_SERVER = environ.get("MAIL_SERVER")
MAIL_PORT = environ.get("MAIL_PORT")
MAIL_USERNAME = environ.get("MAIL_USERNAME")
MAIL_PASSWORD = environ.get("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = environ.get("MAIL_DEFAULT_SENDER")
MAIL_ADMIN = environ.get("MAIL_ADMIN")
MAIL_USE_TLS = False
MAIL_USE_SSL = True

FLASK_PROFILER = {
    "enabled": True,
    "endpointRoot": "profiling",
}
