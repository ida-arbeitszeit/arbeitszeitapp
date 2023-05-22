from typing import Protocol

from arbeitszeit_web.api_presenters.interfaces import JsonDict, JsonString, JsonValue


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


class Unauthorized(Exception):
    code = 401
    description = "Unauthorized"

    def __init__(self, message: str) -> None:
        self.message = message

    @classmethod
    def get_schema(cls) -> JsonValue:
        return JsonDict(
            members=dict(message=JsonString()),
            schema_name="Error",
        )


class BadRequest(Exception):
    code = 400
    description = "Bad Request"

    def __init__(self, message: str) -> None:
        self.message = message

    @classmethod
    def get_schema(cls) -> JsonValue:
        return JsonDict(
            members=dict(message=JsonString()),
            schema_name="Error",
        )
