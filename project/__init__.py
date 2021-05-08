from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    # Switch between production and development configuration
    # app.config.from_object('config.ProdConfig')
    app.config.from_object('config.DevConfig')

    # Where to redirect the user when he attempts to access a login_required
    # view without being logged in.
    login_manager.login_view = 'auth.start'

    # init flask extensions
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():

        # imports like the following may be necessary in order to
        # update changes made to tables in models.
        from .models import Nutzer
        from .models import Betriebe
        from .models import Auszahlungen
        from .models import Kaeufe
        from .models import Kooperationen
        from .models import KooperationenMitglieder

        @login_manager.user_loader
        def load_user(user_id):
            """
            This callback is used to reload the user object from the user ID
            stored in the session.
            """
            user_type = session["user_type"]
            if user_type == "nutzer":
                return Nutzer.query.get(int(user_id))
            elif user_type == "betrieb":
                return Betriebe.query.get(int(user_id))

        # register blueprints
        from .auth import routes as auth_routes
        from .betriebe import routes as betriebe_routes
        from .nutzer import routes as nutzer_routes
        app.register_blueprint(auth_routes.auth)
        app.register_blueprint(betriebe_routes.main_betriebe)
        app.register_blueprint(nutzer_routes.main_nutzer)

        # create the initial database
        db.create_all()

        return app
