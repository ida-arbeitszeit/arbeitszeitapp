from flask_restx import Namespace

from arbeitszeit_flask.api.schema_converter import SchemaConverter
from arbeitszeit_web.api.presenters.response_errors import ApiResponseError


def handle_exception(error: ApiResponseError):
    return {"message": error.message}, error.code


class error_response_handling:
    def __init__(
        self, error_responses: list[type[ApiResponseError]], namespace: Namespace
    ) -> None:
        self._error_responses = error_responses
        self._namespace = namespace
        self._register_error_handlers()

    def __call__(self, original_function):
        return self._add_documention_of_error_responses(original_function)

    def _register_error_handlers(self) -> None:
        for error in self._error_responses:
            self._namespace.error_handlers[error] = handle_exception

    def _add_documention_of_error_responses(self, original_function):
        decorated_fn = original_function
        for response in self._error_responses:
            error_schema = SchemaConverter(self._namespace).json_schema_to_flaskx(
                schema=response.get_schema()
            )
            decorator = self._namespace.response(
                code=response.code, description=response.description, model=error_schema
            )
            decorated_fn = decorator(decorated_fn)
        return decorated_fn
