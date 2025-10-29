import os

FLASK_DEBUG = 0
TESTING = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
LANGUAGES = {"en": "English", "de": "Deutsch", "es": "Español"}
MAIL_PLUGIN_MODULE = "arbeitszeit_flask.mail_service.flask_mail_service"
MAIL_PLUGIN_CLASS = "FlaskMailService"
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_PORT = 587
FORCE_HTTPS = True
AUTO_MIGRATE = os.getenv("AUTO_MIGRATE", False)
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

ALEMBIC_CONFIG = os.getenv("ALEMBIC_CONFIG")
DEFAULT_USER_TIMEZONE = "UTC"
