# type: ignore

from flask import Flask
from werkzeug.middleware.profiler import ProfilerMiddleware


def show_profile_info(app):
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])


def initialize_flask_profiler(app: Flask) -> None:
    try:
        import flask_profiler
    except ImportError:
        return
    flask_profiler.init_app(app)
