from os import environ

from arbeitszeit_flask.configuration_base import *

FLASK_ENV = "production"
DEBUG = False
TESTING = False
# using heroku's existing env variable
SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
# setting secret key from bash with: heroku config:set MY_SECRET_KEY=...
SECRET_KEY = environ.get("MY_SECRET_KEY")

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
REMEMBER_COOKIE_SECURE = True
REMEMBER_COOKIE_HTTPONLY = True

# mail

MAIL_BACKEND = "flask_mail"
MAIL_SERVER = environ.get("MAIL_SERVER")
MAIL_PORT = environ.get("MAIL_PORT")
MAIL_USERNAME = environ.get("MAIL_USERNAME")
MAIL_PASSWORD = environ.get("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = environ.get("MAIL_DEFAULT_SENDER")
MAIL_USE_TLS = False
MAIL_USE_SSL = True
