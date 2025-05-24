import os
from typing import Any

from flask import Flask, session
from flask_talisman import Talisman
from jinja2 import StrictUndefined

from arbeitszeit_flask.babel import initialize_babel
from arbeitszeit_flask.database.db import Database
from arbeitszeit_flask.database.models import Base
from arbeitszeit_flask.datetime import RealtimeDatetimeService
from arbeitszeit_flask.extensions import csrf_protect, login_manager
from arbeitszeit_flask.filters import icon_filter
from arbeitszeit_flask.mail_service import load_email_plugin
from arbeitszeit_flask.migrations.auto_migrate import auto_migrate
from arbeitszeit_flask.profiling import (  # type: ignore
    initialize_flask_profiler,
    show_profile_info,
)


def load_configuration(app: Flask, configuration: Any = None) -> None:
    """Load the right configuration files for the application.

    We will try to load the configuration from top to bottom and use
    the first one that we can find:
    - Load configuration passed into create_app
    - Load from path ARBEITSZEITAPP_CONFIGURATION_PATH
    - Load from path /etc/arbeitszeitapp/arbeitszeitapp.py
    """
    app.config.from_object("arbeitszeit_flask.configuration_base")
    if configuration:
        app.config.from_object(configuration)
    elif config_path := os.environ.get("ARBEITSZEITAPP_CONFIGURATION_PATH"):
        app.config.from_pyfile(config_path)
    else:
        app.config.from_pyfile("/etc/arbeitszeitapp/arbeitszeitapp.py", silent=True)


def create_app(
    config: Any = None,
    template_folder: Any = None,
) -> Flask:
    if template_folder is None:
        template_folder = "templates"

    app = Flask(
        __name__, instance_relative_config=False, template_folder=template_folder
    )

    load_configuration(app=app, configuration=config)

    db = Database()
    db.configure(uri=app.config["SQLALCHEMY_DATABASE_URI"])

    # Choose between auto-migration or direct table creation
    if app.config["AUTO_MIGRATE"]:
        # Let Alembic handle table creation
        auto_migrate(app.config, db)
    else:
        # Create tables directly with SQLAlchemy if they do not exist.
        # These table creations are NOT rolled back in tests for performance reasons
        Base.metadata.create_all(db.engine, checkfirst=True)

    # Where to redirect the user when he attempts to access a login_required
    load_email_plugin(app)

    # Where to redirect the user when he attempts to access a login_required
    # view without being logged in.
    login_manager.login_view = "auth.start"

    if app.config["DEBUG"]:
        app.jinja_env.undefined = StrictUndefined
    else:
        # Init Flask-Talisman
        csp = {"default-src": ["'self'", "'unsafe-inline'"]}
        Talisman(
            app, content_security_policy=csp, force_https=app.config["FORCE_HTTPS"]
        )

    # init flask extensions
    csrf_protect.init_app(app)
    login_manager.init_app(app)
    initialize_babel(app)

    @app.teardown_appcontext
    def shutdown_session(exception: BaseException | None = None) -> None:
        db.session.remove()

    # Set up template filters
    app.template_filter()(RealtimeDatetimeService().format_datetime)
    app.template_filter("icon")(icon_filter)

    with app.app_context():
        from arbeitszeit_flask.commands import invite_accountant

        app.cli.command("invite-accountant")(invite_accountant)

        from .database.models import Accountant, Company, Member

        @login_manager.user_loader
        def load_user(user_id: Any) -> Any:
            """
            This callback is used to reload the user object from the user ID
            stored in the session.
            """
            if "user_type" in session:
                user_type = session["user_type"]
                if user_type == "member":
                    return db.session.query(Member).get(user_id)
                elif user_type == "company":
                    return db.session.query(Company).get(user_id)
                elif user_type == "accountant":
                    return db.session.query(Accountant).get(user_id)

        # register blueprints
        from . import accountant, company, member, user
        from .api import blueprint as api_blueprint
        from .auth import routes as auth_routes
        from .context_processors import add_template_variables
        from .plots import routes as plots_routes

        app.register_blueprint(auth_routes.auth)
        app.register_blueprint(plots_routes.plots)
        app.register_blueprint(company.blueprint.main_company, url_prefix="/company")
        app.register_blueprint(member.blueprint.main_member, url_prefix="/member")
        app.register_blueprint(accountant.blueprint.main_accountant)
        app.register_blueprint(user.blueprint, url_prefix="/user")
        app.register_blueprint(api_blueprint)
        app.context_processor(add_template_variables)

        if app.config["DEBUG_DETAILS"] == True:
            show_profile_info(app)

        # The profiler needs to be initialized last because all the
        # routes to monitor need to present in the app at that point
        initialize_flask_profiler(app)

        return app
