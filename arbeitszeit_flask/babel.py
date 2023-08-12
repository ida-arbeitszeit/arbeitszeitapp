from typing import Any

from flask import Flask, current_app, request, session
from flask_babel import Babel


def initialize_babel(app: Flask) -> None:
    if _initialize_babel_3_x(app):
        return
    _initialize_babel_2_x(app)


def _initialize_babel_2_x(app: Flask) -> None:
    babel = Babel(app)
    babel.localeselector(get_locale)  # type: ignore


def _initialize_babel_3_x(app: Flask) -> bool:
    try:
        Babel(app, locale_selector=get_locale)
    except TypeError:
        return False
    return True


def get_locale() -> Any:
    try:
        return session["language"]
    except KeyError:
        return request.accept_languages.best_match(
            current_app.config["LANGUAGES"].keys()
        )
