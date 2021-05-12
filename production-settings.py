from os import environ

from project.configuration_base import *


FLASK_ENV = "production"
DEBUG = False
TESTING = False
# using heroku's existing env variable
SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
# setting secret key from bash with: heroku config:set MY_SECRET_KEY=...
SECRET_KEY = environ.get("MY_SECRET_KEY")
