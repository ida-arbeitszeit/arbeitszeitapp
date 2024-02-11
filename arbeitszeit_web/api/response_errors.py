"""
The exceptions in this module are ordered by their HTTP status code.
"""

from typing import Protocol

from arbeitszeit_web.api.presenters.interfaces import JsonObject, JsonString, JsonValue


class ApiResponseError(Protocol):
    def __init__(self, message: str) -> None:
        ...

    @property
    def code(self) -> int:  # must be class var
        ...

    @property
    def description(self) -> str:  # must be class var
        ...

    @classmethod
    def get_schema(cls) -> JsonValue:
        ...

    @property
    def message(self) -> str:
        ...


error_response_schema = JsonObject(
    members=dict(message=JsonString()),
    name="Error",
)


class BadRequest(Exception):
    code = 400
    description = "Bad Request"

    def __init__(self, message: str) -> None:
        self.message = message

    @classmethod
    def get_schema(cls) -> JsonValue:
        return error_response_schema


class Unauthorized(Exception):
    code = 401
    description = "Unauthorized"

    def __init__(self, message: str) -> None:
        self.message = message

    @classmethod
    def get_schema(cls) -> JsonValue:
        return error_response_schema


class Forbidden(Exception):
    code = 403
    description = "Forbidden"

    def __init__(self, message: str) -> None:
        self.message = message

    @classmethod
    def get_schema(cls) -> JsonValue:
        return error_response_schema


class NotFound(Exception):
    code = 404
    description = "Not Found"

    def __init__(self, message: str) -> None:
        self.message = message

    @classmethod
    def get_schema(cls) -> JsonValue:
        return error_response_schema
