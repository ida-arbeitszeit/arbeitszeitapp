import os
from typing import Any, Optional

from flask import Flask, session
from flask_migrate import upgrade
from flask_talisman import Talisman

import arbeitszeit_flask.extensions
from arbeitszeit_flask.babel import initialize_babel
from arbeitszeit_flask.datetime import RealtimeDatetimeService
from arbeitszeit_flask.extensions import csrf_protect, login_manager, mail
from arbeitszeit_flask.profiling import (  # type: ignore
    initialize_flask_profiler,
    show_profile_info,
    show_sql_queries,
)


def load_configuration(app: Any, configuration: Optional[Any] = None) -> None:
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


def initialize_migrations(app: Any, db: Any) -> None:
    migrate = arbeitszeit_flask.extensions.migrate
    migrations_directory = os.path.join(os.path.dirname(__file__), "migrations")
    migrate.init_app(app, db, directory=migrations_directory)
    if app.config["AUTO_MIGRATE"]:
        with app.app_context():
            upgrade(migrations_directory)


def create_app(config: Any = None, db: Any = None, template_folder: Any = None) -> Any:
    if template_folder is None:
        template_folder = "templates"

    app = Flask(
        __name__, instance_relative_config=False, template_folder=template_folder
    )

    load_configuration(app=app, configuration=config)

    if db is None:
        db = arbeitszeit_flask.extensions.db

    # Where to redirect the user when he attempts to access a login_required
    # view without being logged in.
    login_manager.login_view = "auth.start"

    # Init Flask-Talisman
    if not app.config["DEBUG"]:
        csp = {"default-src": ["'self'", "'unsafe-inline'", "*.fontawesome.com"]}
        Talisman(
            app, content_security_policy=csp, force_https=app.config["FORCE_HTTPS"]
        )

    # init flask extensions
    csrf_protect.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    initialize_migrations(app=app, db=db)
    mail.init_app(app)
    initialize_babel(app)

    # Setup template filter
    app.template_filter()(RealtimeDatetimeService().format_datetime)

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
                    return Member.query.get(user_id)
                elif user_type == "company":
                    return Company.query.get(user_id)
                elif user_type == "accountant":
                    return Accountant.query.get(user_id)

        # register blueprints
        from . import accountant, company, member
        from .api import blueprint as api_blueprint
        from .auth import routes as auth_routes
        from .context_processors import add_template_variables
        from .plots import routes as plots_routes

        app.register_blueprint(auth_routes.auth)
        app.register_blueprint(plots_routes.plots)
        app.register_blueprint(company.blueprint.main_company)
        app.register_blueprint(member.blueprint.main_member)
        app.register_blueprint(accountant.blueprint.main_accountant)
        app.register_blueprint(api_blueprint)
        app.context_processor(add_template_variables)

        if app.config["DEBUG_DETAILS"] == True:
            show_profile_info(app)
            show_sql_queries(app)

        # The profiler needs to be initialized last because all the
        # routes to monitor need to present in the app at that point
        initialize_flask_profiler(app)

        return app
