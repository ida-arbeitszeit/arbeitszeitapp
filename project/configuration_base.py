from os import environ

"""Base config."""
STATIC_FOLDER = "static"
TEMPLATES_FOLDER = "templates"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT")
