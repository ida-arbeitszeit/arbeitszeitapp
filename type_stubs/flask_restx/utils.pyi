from _typeshed import Incomplete

__all__ = [
    "merge",
    "camel_to_dash",
    "default_id",
    "not_none",
    "not_none_sorted",
    "unpack",
    "BaseResponse",
    "import_check_view_func",
]

BaseResponse: Incomplete

class FlaskCompatibilityWarning(DeprecationWarning): ...

def merge(first, second): ...
def camel_to_dash(value): ...
def default_id(resource, method): ...
def not_none(data): ...
def not_none_sorted(data): ...
def unpack(response, default_code=...): ...
def import_check_view_func(): ...
