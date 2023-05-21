from flask_restx import Namespace

from arbeitszeit_flask.api.schema_converter import json_schema_to_flaskx
from arbeitszeit_web.api_presenters.response_errors import ApiResponseError


class with_response_documentation:
    def __init__(
        self, error_responses: list[type[ApiResponseError]], namespace: Namespace
    ) -> None:
        self._error_responses = error_responses
        self._namespace = namespace

    def __call__(self, original_function):
        decorated_fn = original_function
        for response in self._error_responses:
            error_schema = json_schema_to_flaskx(
                schema=response.get_schema(), namespace=self._namespace
            )
            decorator = self._namespace.response(
                code=response.code, description=response.description, model=error_schema
            )
            decorated_fn = decorator(decorated_fn)
        return decorated_fn
