from flask import Flask

from arbeitszeit_development.dev_cli import fic, generate
from arbeitszeit_flask import create_app


def main() -> Flask:
    app = create_app()
    app.cli.add_command(generate)
    app.cli.add_command(fic)
    return app
