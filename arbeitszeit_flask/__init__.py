import click
from flask import Flask, current_app, request, session
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

import arbeitszeit_flask.extensions
from arbeitszeit_flask.datetime import RealtimeDatetimeService
from arbeitszeit_flask.extensions import babel, login_manager, mail
from arbeitszeit_flask.profiling import show_profile_info, show_sql_queries


def create_app(config=None, db=None, migrate=None, template_folder=None):
    if template_folder is None:
        template_folder = "templates"

    app = Flask(
        __name__, instance_relative_config=False, template_folder=template_folder
    )

    if config:
        app.config.update(**config)
    else:
        app.config.from_envvar("ARBEITSZEIT_APP_CONFIGURATION")

    if db is None:
        db = arbeitszeit_flask.extensions.db

    if migrate is None:
        migrate = arbeitszeit_flask.extensions.migrate

    # Where to redirect the user when he attempts to access a login_required
    # view without being logged in.
    login_manager.login_view = "auth.start"

    # Init Flask-Talisman
    if app.config["ENV"] == "production":
        csp = {"default-src": ["'self'", "'unsafe-inline'", "*.fontawesome.com"]}
        Talisman(app, content_security_policy=csp)

    # init flask extensions
    CSRFProtect(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    babel.init_app(app)

    # Setup template filter
    app.template_filter()(RealtimeDatetimeService().format_datetime)

    with app.app_context():

        from arbeitszeit_flask.commands import (
            invite_accountant,
            trans_compile,
            trans_new,
            trans_update,
            update_and_payout,
        )

        app.cli.command("payout")(update_and_payout)
        app.cli.command("trans-update")(trans_update)
        app.cli.command("trans-compile")(trans_compile)
        app.cli.command("trans-new")(click.argument("lang_code")(trans_new))
        app.cli.command("invite-accountant")(invite_accountant)

        from .models import Company, Member

        @login_manager.user_loader
        def load_user(user_id):
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

        # register blueprints
        from . import company, member
        from .auth import routes as auth_routes
        from .plots import routes as plots_routes

        app.register_blueprint(auth_routes.auth)
        app.register_blueprint(plots_routes.plots)
        app.register_blueprint(company.blueprint.main_company)
        app.register_blueprint(member.blueprint.main_member)

        if app.config["ENV"] == "development":
            if app.config["DEBUG_DETAILS"] == True:
                # print profiling info to sys.stout
                show_profile_info(app)
                show_sql_queries(app)

        return app


@babel.localeselector
def get_locale():
    try:
        return session["language"]
    except KeyError:
        return request.accept_languages.best_match(
            current_app.config["LANGUAGES"].keys()
        )
