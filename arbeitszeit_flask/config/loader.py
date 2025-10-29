import os
from typing import Any

from flask import Flask


def load_configuration(app: Flask, configuration: Any = None) -> None:
    """Load the right configuration for the application.

    First we load the base configuration from arbeitszeit_flask.config.configuration_base.

    Then, on top of this, we load the first configuration we can find from the following sources
    from top to bottom:
    - Configuration passed into create_app
    - From path ARBEITSZEITAPP_CONFIGURATION_PATH
    - From path /etc/arbeitszeitapp/arbeitszeitapp.py
    """
    app.config.from_object("arbeitszeit_flask.config.configuration_base")
    if configuration:
        app.config.from_object(configuration)
    elif config_path := os.environ.get("ARBEITSZEITAPP_CONFIGURATION_PATH"):
        app.config.from_pyfile(config_path)
    else:
        app.config.from_pyfile("/etc/arbeitszeitapp/arbeitszeitapp.py", silent=True)
