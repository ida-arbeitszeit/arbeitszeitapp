"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    """Base config."""
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    """Config for production on heroku."""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    # using heroku's existing env variable
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    # setting secret key from bash with: heroku config:set MY_SECRET_KEY=...
    SECRET_KEY = environ.get('MY_SECRET_KEY')


class DevConfig(Config):
    """Config for development"""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URI')
    SQLALCHEMY_ECHO = False
    SECRET_KEY = environ.get('DEV_SECRET_KEY')
