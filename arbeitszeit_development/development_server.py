from flask import Flask

from arbeitszeit_development.dev_cli import generate
from arbeitszeit_flask import create_app


def main() -> Flask:
    app = create_app()
    app.cli.add_command(generate)
    return app
