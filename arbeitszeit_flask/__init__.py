from typing import Any

from flask import Flask, session
from flask_talisman import Talisman
from jinja2 import StrictUndefined

from arbeitszeit_db.db import Database
from arbeitszeit_flask.babel import initialize_babel
from arbeitszeit_flask.config.checks import ConfigValidator
from arbeitszeit_flask.config.loader import load_configuration
from arbeitszeit_flask.config.options import CONFIG_OPTIONS
from arbeitszeit_flask.database import run_db_migrations
from arbeitszeit_flask.extensions import csrf_protect, login_manager
from arbeitszeit_flask.filters import icon_filter
from arbeitszeit_flask.flask_session import FlaskLoginUser
from arbeitszeit_flask.mail_service import load_email_plugin
from arbeitszeit_flask.profiling import initialize_flask_profiler  # type: ignore


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

    config_validator = ConfigValidator(app.config, CONFIG_OPTIONS)
    config_validator.validate_options()
    config_validator.validate_option_types()

    db = Database()
    db.configure(
        uri=app.config.get(
            "SQLALCHEMY_DATABASE_URI", "sqlite:////tmp/arbeitszeitapp.db"
        )
    )
    run_db_migrations(app.config, db)

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

    app.template_filter("icon")(icon_filter)

    with app.app_context():
        from arbeitszeit_flask.commands import invite_accountant

        app.cli.command("invite-accountant")(invite_accountant)

        from arbeitszeit_db.models import Accountant, Company, Member

        @login_manager.user_loader
        def load_user(
            user_id: str,
        ) -> FlaskLoginUser | None:
            """
            This callback is used to reload the user object from the user ID
            stored in the session.
            """
            if "user_type" in session:
                user_type = session["user_type"]
                if user_type == "member":
                    member_orm = db.session.query(Member).get(user_id)
                    return FlaskLoginUser(member_orm) if member_orm else None
                elif user_type == "company":
                    company_orm = db.session.query(Company).get(user_id)
                    return FlaskLoginUser(company_orm) if company_orm else None
                elif user_type == "accountant":
                    accountant_orm = db.session.query(Accountant).get(user_id)
                    return FlaskLoginUser(accountant_orm) if accountant_orm else None
            return None

        # register blueprints
        from .api import blueprint as api_blueprint
        from .context_processors import add_template_variables
        from .plots import routes as plots_routes
        from .routes import accountant as accountant_routes
        from .routes import company as company_routes
        from .routes import healthcheck as healthcheck_routes
        from .routes import member as member_routes
        from .routes import user as user_routes
        from .routes.auth import routes as auth_routes

        app.register_blueprint(auth_routes.auth)
        app.register_blueprint(plots_routes.plots)
        app.register_blueprint(
            company_routes.blueprint.main_company, url_prefix="/company"
        )
        app.register_blueprint(
            member_routes.blueprint.main_member, url_prefix="/member"
        )
        app.register_blueprint(accountant_routes.blueprint.main_accountant)
        app.register_blueprint(user_routes.blueprint, url_prefix="/user")
        app.register_blueprint(api_blueprint)
        app.register_blueprint(healthcheck_routes.blueprint.healthcheck_blueprint)
        app.context_processor(add_template_variables)

        # The profiler needs to be initialized last because all the
        # routes to monitor need to present in the app at that point
        initialize_flask_profiler(app)

        return app
