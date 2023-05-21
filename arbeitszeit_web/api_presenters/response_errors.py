from abc import ABC, abstractproperty

from arbeitszeit_web.api_presenters.interfaces import JsonDict, JsonString, JsonValue


class ApiResponseError(ABC):
    @classmethod
    def get_schema(cls) -> JsonValue:
        return JsonDict(
            members=dict(message=JsonString()),
            schema_name="Error",
        )

    @abstractproperty
    def code(self) -> int:
        pass

    @abstractproperty
    def description(self) -> str:
        pass


class Unauthorized(ApiResponseError, Exception):
    code = 401
    description = "Unauthorized"

    def __init__(self, message: str) -> None:
        self.message = message


class BadRequest(ApiResponseError, Exception):
    code = 400
    description = "Bad Request"

    def __init__(self, message: str) -> None:
        self.message = message
