from os import environ

TESTING = False
# using heroku's existing env variable
# (SQLAlchemy 1.4.x has removed support for the postgres:// URI scheme, which is used by Heroku Postgres)
SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
assert SQLALCHEMY_DATABASE_URI
if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
        "postgres://", "postgresql://", 1
    )
# setting secret key from bash with: heroku config:set MY_SECRET_KEY=...
SECRET_KEY = environ.get("MY_SECRET_KEY")
SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT")
SERVER_NAME = environ.get("ARBEITSZEIT_APP_SERVER_NAME")
STATIC_FOLDER = "static"
TEMPLATES_FOLDER = "templates"

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
