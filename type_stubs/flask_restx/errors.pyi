from _typeshed import Incomplete

__all__ = ["abort", "RestError", "ValidationError", "SpecsError"]

def abort(code=..., message: Incomplete | None = None, **kwargs) -> None: ...

class RestError(Exception):
    msg: Incomplete
    def __init__(self, msg) -> None: ...

class ValidationError(RestError): ...
class SpecsError(RestError): ...
