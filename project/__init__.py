from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import project.my_database_key as db_key

# init SQLAlchemy
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_key.username}:{db_key.password}@localhost/betriebe2'
    login_manager.login_view = 'auth.start'

    login_manager.init_app(app)
    db.init_app(app)

    from .models import Nutzer
    from .models import Betriebe

    @login_manager.user_loader
    def load_user(user_id):
        user_type = session["user_type"]
        if user_type == "nutzer":
            return Nutzer.query.get(int(user_id))
        elif user_type == "betrieb":
            return Betriebe.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main_nutzer import main_nutzer as main_nutzer_blueprint
    app.register_blueprint(main_nutzer_blueprint)

    from .main_betriebe import main_betriebe as main_betriebe_blueprint
    app.register_blueprint(main_betriebe_blueprint)

    return app
