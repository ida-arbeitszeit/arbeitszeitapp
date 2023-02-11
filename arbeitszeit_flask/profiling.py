# type: ignore
from __future__ import annotations

from typing import Dict

from flask import Flask, Response, request
from werkzeug.middleware.profiler import ProfilerMiddleware

try:
    from flask_sqlalchemy.record_queries import _QueryInfo, get_recorded_queries

    def show_sql_queries(app):
        @app.after_request
        def after_request(response: Response) -> Response:
            queries: Dict[str, int] = dict()
            for query in get_recorded_queries():
                queries = _update_queries_dict(queries, query)

            if queries:
                _print_queries(queries)
            return response

    def _update_queries_dict(queries: Dict[str, int], query: _QueryInfo):
        if queries.get(query.location) is not None:
            queries[query.location] += 1
        else:
            queries[query.location] = 1
        return queries

    def _print_queries(queries):
        print()
        print("SqlAlchemy queries")
        print("===================")
        print(f"Route: {request.path}. Method: {request.method}")
        print("QueryCount", " Location")
        for location in sorted(queries, key=queries.__getitem__, reverse=True):
            print("{:>10}  {:<0}".format(queries[location], location))
        print()

except ModuleNotFoundError:
    from flask_sqlalchemy import get_debug_queries

    def show_sql_queries(app):
        @app.after_request
        def after_request(response: Response) -> Response:
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


def show_profile_info(app):
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])


def initialize_flask_profiler(app: Flask) -> None:
    try:
        import flask_profiler
    except ImportError:
        return
    flask_profiler.init_app(app)
