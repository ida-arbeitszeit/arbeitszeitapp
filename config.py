"""Flask configuration."""
# import project.my_database_key as db_key

# from os import environ, path
# from dotenv import load_dotenv
#
# basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))


class Config:
    """Set Flask config variables."""

    # FLASK_ENV = 'development'
    # TESTING = True
    SECRET_KEY = b'\xb1:\x7f/X\xfd\x9e\xe4)`\xc0\x88\x80\xad\xecK'
    # SECRET_KEY = environ.get('SECRET_KEY')
    # STATIC_FOLDER = 'static'
    # TEMPLATES_FOLDER = 'templates'

    # Database
    #SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = "postgres://nqursisgweipja:f08c53bd55db7e83a2a8b5837b9aae32ada35e83e32176a9172352bbf252b291@ec2-54-76-215-139.eu-west-1.compute.amazonaws.com:5432/deh13a0u5h8jkm"
    # SQLALCHEMY_DATABASE_URI = f'postgresql://{db_key.username}:{db_key.password}@localhost/betriebe2'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS Secrets
    # AWS_SECRET_KEY = environ.get('AWS_SECRET_KEY')
    # AWS_KEY_ID = environ.get('AWS_KEY_ID')
