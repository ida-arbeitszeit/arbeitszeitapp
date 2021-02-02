from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_table import Table, Col

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=False)

    # Production/Development configuration
    app.config.from_object('config.ProdConfig')
    # app.config.from_object('config.DevConfig')

    login_manager.login_view = 'auth.start'

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():

        from .models import Nutzer
        from .models import Betriebe
        from .models import Auszahlungen

        @login_manager.user_loader
        def load_user(user_id):
         user_type = session["user_type"]
         if user_type == "nutzer":
             return Nutzer.query.get(int(user_id))
         elif user_type == "betrieb":
             return Betriebe.query.get(int(user_id))

        from .auth import routes as auth_routes
        from .betriebe import routes as betriebe_routes
        from .nutzer import routes as nutzer_routes
        app.register_blueprint(auth_routes.auth)
        app.register_blueprint(betriebe_routes.main_betriebe)
        app.register_blueprint(nutzer_routes.main_nutzer)

        db.create_all()

        return app
