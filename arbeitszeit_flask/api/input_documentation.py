from typing import Callable, Sequence

from flask_restx import Namespace
from flask_restx.reqparse import RequestParser

from arbeitszeit_web.api.controllers.parameters import (
    BodyParameter,
    PathParameter,
    QueryParameter,
)


class with_input_documentation:
    def __init__(
        self,
        expected_inputs: Sequence[QueryParameter | BodyParameter | PathParameter],
        namespace: Namespace,
    ) -> None:
        self._expected_inputs = expected_inputs
        self._namespace = namespace

    def __call__(self, func: Callable) -> Callable:
        parser = RequestParser()
        for expected_input in self._expected_inputs:
            if isinstance(expected_input, PathParameter):
                # RequestParser does not handle path parameters
                # https://github.com/noirbizarre/flask-restplus/issues/146
                self._add_documentation_for_path_variable(func, expected_input)
            else:
                parser = self._add_argument_to_parser(parser, expected_input)
        decorator = self._namespace.doc(expect=[parser])
        decorator(func)
        return func

    def _add_documentation_for_path_variable(
        self, func: Callable, expected_input: PathParameter
    ) -> None:
        decorator = self._namespace.doc(
            params={expected_input.name: expected_input.description}
        )
        decorator(func)

    def _add_argument_to_parser(
        self, parser: RequestParser, input: BodyParameter | QueryParameter
    ) -> RequestParser:
        location = "query" if isinstance(input, QueryParameter) else "json"
        return parser.add_argument(
            name=input.name,
            type=input.type,
            help=input.description,
            default=input.default,
            location=location,
            required=input.required,
        )
