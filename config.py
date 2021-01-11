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
    SQLALCHEMY_DATABASE_URI = "postgres://vafeqodbfvitgv:90a92c73899e009283cc949375ad7d6a7f25f39ee122a20ca6818396eac6b098@ec2-52-211-108-161.eu-west-1.compute.amazonaws.com:5432/d9vli47sdpq0if"
    # SQLALCHEMY_DATABASE_URI = f'postgresql://{db_key.username}:{db_key.password}@localhost/betriebe2'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS Secrets
    # AWS_SECRET_KEY = environ.get('AWS_SECRET_KEY')
    # AWS_KEY_ID = environ.get('AWS_KEY_ID')
