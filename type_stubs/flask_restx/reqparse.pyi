from ._http import HTTPStatus as HTTPStatus
from .errors import SpecsError as SpecsError, abort as abort
from .marshalling import marshal as marshal
from .model import Model as Model
from _typeshed import Incomplete

class ParseResult(dict):
    def __getattr__(self, name): ...
    def __setattr__(self, name, value) -> None: ...

LOCATIONS: Incomplete
PY_TYPES: Incomplete
SPLIT_CHAR: str

class Argument:
    name: Incomplete
    default: Incomplete
    dest: Incomplete
    required: Incomplete
    ignore: Incomplete
    location: Incomplete
    type: Incomplete
    choices: Incomplete
    action: Incomplete
    help: Incomplete
    case_sensitive: Incomplete
    operators: Incomplete
    store_missing: Incomplete
    trim: Incomplete
    nullable: Incomplete
    def __init__(self, name, default: Incomplete | None = ..., dest: Incomplete | None = ..., required: bool = ..., ignore: bool = ..., type=..., location=..., choices=..., action: str = ..., help: Incomplete | None = ..., operators=..., case_sensitive: bool = ..., store_missing: bool = ..., trim: bool = ..., nullable: bool = ...) -> None: ...
    def source(self, request): ...
    def convert(self, value, op): ...
    def handle_validation_error(self, error, bundle_errors): ...
    def parse(self, request, bundle_errors: bool = ...): ...
    @property
    def __schema__(self): ...

class RequestParser:
    args: Incomplete
    argument_class: Incomplete
    result_class: Incomplete
    trim: Incomplete
    bundle_errors: Incomplete
    def __init__(self, argument_class=..., result_class=..., trim: bool = ..., bundle_errors: bool = ...) -> None: ...
    def add_argument(self, *args, **kwargs): ...
    def parse_args(self, req: Incomplete | None = ..., strict: bool = ...): ...
    def copy(self): ...
    def replace_argument(self, name, *args, **kwargs): ...
    def remove_argument(self, name): ...
    @property
    def __schema__(self): ...
