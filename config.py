"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    """Base config."""
    SECRET_KEY = b'\xb1:\x7f/X\xfd\x9e\xe4)`\xc0\x88\x80\xad\xecK'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = "postgres://vafeqodbfvitgv:90a92c73899e009283cc949375ad7d6a7f25f39ee122a20ca6818396eac6b098@ec2-52-211-108-161.eu-west-1.compute.amazonaws.com:5432/d9vli47sdpq0if"


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URI')
