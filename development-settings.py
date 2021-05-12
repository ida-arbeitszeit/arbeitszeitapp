from os import environ, path

from dotenv import load_dotenv

from project.configuration_base import *

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

FLASK_ENV = "development"
DEBUG = True
TESTING = True
SQLALCHEMY_DATABASE_URI = environ.get("DEV_DATABASE_URI")
SQLALCHEMY_ECHO = False
SECRET_KEY = environ.get("DEV_SECRET_KEY")
