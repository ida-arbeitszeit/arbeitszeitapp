from flask import Flask

from arbeitszeit_flask import create_app
from tests.flask_integration.dev_cli import generate


def main() -> Flask:
    app = create_app()
    app.cli.add_command(generate)
    return app
