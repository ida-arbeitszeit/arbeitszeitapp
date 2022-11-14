from typing import Dict

from flask import Flask
from flask_sqlalchemy import get_debug_queries
from werkzeug.middleware.profiler import ProfilerMiddleware


def show_profile_info(app):
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])


def show_sql_queries(app):
    @app.after_request
    def after_request(response):
        queries: Dict[int, int] = dict()
        for query in get_debug_queries():
            queries = _update_queries_dict(queries, query)

        _print_queries(queries)
        return response


def _update_queries_dict(queries, query):
    if queries.get(query.context) is not None:
        queries[query.context] += 1
    else:
        queries[query.context] = 1
    return queries


def _print_queries(queries):
    print()
    print("SQLAlCHEMY COUNT QUERIES:")
    print("=========================")
    print("QueryCount", " Context")
    for context in sorted(queries, key=queries.__getitem__, reverse=True):
        print("{:>10}  {:<0}".format(queries[context], context))
    print()


def initialize_flask_profiler(app: Flask) -> None:
    try:
        import flask_profiler
    except ImportError:
        return
    flask_profiler.init_app(app)
