from os import environ

FLASK_DEBUG = 0
DEBUG_DETAILS = False
TESTING = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/arbeitszeitapp.db"
SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT")
LANGUAGES = {"en": "English", "de": "Deutsch"}
MAIL_PORT = "25"
FORCE_HTTPS = True
AUTO_MIGRATE = False

# control thresholds
ALLOWED_OVERDRAW_MEMBER = "0"
ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION = "33"

FLASK_PROFILER = {
    "enabled": False,
}

RESTX_MASK_SWAGGER = False