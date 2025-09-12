from os import environ

FLASK_DEBUG = 0
DEBUG_DETAILS = False
TESTING = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = environ.get(
    "ARBEITSZEITAPP_DATABASE_URI", "sqlite:////tmp/arbeitszeitapp.db"
)
SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT")
LANGUAGES = {"en": "English", "de": "Deutsch", "es": "Español"}
MAIL_PORT = "25"
FORCE_HTTPS = True
AUTO_MIGRATE = False
PREFERRED_URL_SCHEME = "https"

# control thresholds
ALLOWED_OVERDRAW_MEMBER = "0"
ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION = "33"

FLASK_PROFILER = {
    "enabled": False,
}

RESTX_MASK_SWAGGER = False
ARBEITSZEIT_PASSWORD_HASHER = "arbeitszeit_flask.password_hasher:PasswordHasherImpl"

# swagger placeholders are necessary until fix of bug in flask-restx:
# https://github.com/python-restx/flask-restx/issues/565
SWAGGER_UI_OAUTH_CLIENT_ID = "placeholder"
SWAGGER_VALIDATOR_URL = "placeholder"
SWAGGER_UI_OAUTH_REALM = "placeholder"
SWAGGER_UI_OAUTH_APP_NAME = "placeholder"

# Path to the alembic configuration file relative to the working directory of
# the flask process.
ALEMBIC_CONFIGURATION_FILE = "alembic.ini"
DEFAULT_USER_TIMEZONE = "UTC"
