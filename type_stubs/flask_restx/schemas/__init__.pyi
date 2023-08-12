from _typeshed import Incomplete
from collections.abc import Mapping
from flask_restx import errors as errors

class SchemaValidationError(errors.ValidationError):
    errors: Incomplete
    def __init__(self, msg, errors: Incomplete | None = ...) -> None: ...
    __unicode__: Incomplete

class LazySchema(Mapping):
    filename: Incomplete
    def __init__(self, filename, validator=...) -> None: ...
    def __getitem__(self, key): ...
    def __iter__(self): ...
    def __len__(self) -> int: ...
    @property
    def validator(self): ...

OAS_20: Incomplete
VERSIONS: Incomplete

def validate(data): ...