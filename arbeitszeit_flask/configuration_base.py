from os import environ

DEBUG = False
DEBUG_DETAILS = False
TESTING = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/arbeitszeitapp.db"
SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT")
LANGUAGES = {"en": "English", "de": "Deutsch"}
MAIL_PORT = "25"
