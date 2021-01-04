from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import project.my_database_key as db_key


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_key.username}:{db_key.password}@localhost/betriebe2'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.start'
    login_manager.init_app(app)

    from .models import Nutzer
    from .models import Betriebe

    @login_manager.user_loader
    def load_user(user_id):
        user_type = session["user_type"]
        if user_type == "nutzer":
            # since the user_id is just the primary key of our user table, use it in the query for the user
            return Nutzer.query.get(int(user_id))
        elif user_type == "betrieb":
            return Betriebe.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main_nutzer import main_nutzer as main_nutzer_blueprint
    app.register_blueprint(main_nutzer_blueprint)

    from .main_betriebe import main_betriebe as main_betriebe_blueprint
    app.register_blueprint(main_betriebe_blueprint)

    return app
