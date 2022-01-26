from os import environ, path

from dotenv import load_dotenv

from arbeitszeit_flask.configuration_base import *

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

FLASK_ENV = "development"
DEBUG = True
DEBUG_DETAILS = environ.get("DEBUG_DETAILS") in ("true", "True", "1", "t")
TESTING = True
SQLALCHEMY_DATABASE_URI = environ.get("DEV_DATABASE_URI")
SQLALCHEMY_ECHO = False
SECRET_KEY = environ.get("DEV_SECRET_KEY")

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
REMEMBER_COOKIE_HTTPONLY = True

# mail
MAIL_SERVER = environ.get("MAIL_SERVER")
MAIL_PORT = environ.get("MAIL_PORT")
MAIL_USERNAME = environ.get("MAIL_USERNAME")
MAIL_PASSWORD = environ.get("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = environ.get("MAIL_DEFAULT_SENDER")
MAIL_USE_TLS = False
MAIL_USE_SSL = True
