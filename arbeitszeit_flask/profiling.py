# type: ignore

from flask import Flask


def initialize_flask_profiler(app: Flask) -> None:
    try:
        import flask_profiler
    except ImportError:
        return
    flask_profiler.init_app(app)
