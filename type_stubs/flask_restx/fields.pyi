from _typeshed import Incomplete
from werkzeug.utils import cached_property

from .errors import RestError

__all__ = [
    "Raw",
    "String",
    "FormattedString",
    "Url",
    "DateTime",
    "Date",
    "Boolean",
    "Integer",
    "Float",
    "Arbitrary",
    "Fixed",
    "Nested",
    "List",
    "ClassName",
    "Polymorph",
    "Wildcard",
    "StringMixin",
    "MinMaxMixin",
    "NumberMixin",
    "MarshallingError",
]

class MarshallingError(RestError):
    def __init__(self, underlying_exception) -> None: ...

class Raw:
    __schema_type__: str
    __schema_format__: Incomplete
    __schema_example__: Incomplete
    attribute: Incomplete
    default: Incomplete
    title: Incomplete
    description: Incomplete
    required: Incomplete
    readonly: Incomplete
    example: Incomplete
    mask: Incomplete
    nullable: Incomplete
    def __init__(
        self,
        default=None,
        attribute=None,
        title=None,
        description=None,
        required=None,
        readonly=None,
        example=None,
        mask=None,
        nullable=None,
        **kwargs,
    ) -> None: ...
    def format(self, value): ...
    def output(self, key, obj, **kwargs): ...
    @cached_property
    def __schema__(self): ...
    def schema(self): ...

class Nested(Raw):
    __schema_type__: Incomplete
    model: Incomplete
    as_list: Incomplete
    allow_null: Incomplete
    skip_none: Incomplete
    def __init__(
        self,
        model,
        allow_null: bool = False,
        skip_none: bool = False,
        as_list: bool = False,
        **kwargs,
    ) -> None: ...
    @property
    def nested(self): ...
    def output(self, key, obj, ordered: bool = False, **kwargs): ...
    def schema(self): ...
    def clone(self, mask=None): ...

class List(Raw):
    min_items: Incomplete
    max_items: Incomplete
    unique: Incomplete
    container: Incomplete
    def __init__(self, cls_or_instance, **kwargs) -> None: ...
    def format(self, value): ...
    def output(self, key, data, ordered: bool = False, **kwargs): ...
    def schema(self): ...
    def clone(self, mask=None): ...

class StringMixin:
    __schema_type__: str
    min_length: Incomplete
    max_length: Incomplete
    pattern: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def schema(self): ...

class MinMaxMixin:
    minimum: Incomplete
    exclusiveMinimum: Incomplete
    maximum: Incomplete
    exclusiveMaximum: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def schema(self): ...

class NumberMixin(MinMaxMixin):
    __schema_type__: str
    multiple: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def schema(self): ...

class String(StringMixin, Raw):
    enum: Incomplete
    discriminator: Incomplete
    required: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def format(self, value): ...
    def schema(self): ...

class Integer(NumberMixin, Raw):
    __schema_type__: str
    def format(self, value): ...

class Float(NumberMixin, Raw):
    def format(self, value): ...

class Arbitrary(NumberMixin, Raw):
    def format(self, value): ...

class Fixed(NumberMixin, Raw):
    precision: Incomplete
    def __init__(self, decimals: int = 5, **kwargs) -> None: ...
    def format(self, value): ...

class Boolean(Raw):
    __schema_type__: str
    def format(self, value): ...

class DateTime(MinMaxMixin, Raw):
    __schema_type__: str
    __schema_format__: str
    dt_format: Incomplete
    def __init__(self, dt_format: str = "iso8601", **kwargs) -> None: ...
    def parse(self, value): ...
    def format(self, value): ...
    def format_rfc822(self, dt): ...
    def format_iso8601(self, dt): ...
    def schema(self): ...

class Date(DateTime):
    __schema_format__: str
    def __init__(self, **kwargs) -> None: ...
    def parse(self, value): ...

class Url(StringMixin, Raw):
    endpoint: Incomplete
    absolute: Incomplete
    scheme: Incomplete
    def __init__(
        self, endpoint=None, absolute: bool = False, scheme=None, **kwargs
    ) -> None: ...
    def output(self, key, obj, **kwargs): ...

class FormattedString(StringMixin, Raw):
    src_str: Incomplete
    def __init__(self, src_str, **kwargs) -> None: ...
    def output(self, key, obj, **kwargs): ...

class ClassName(String):
    dash: Incomplete
    def __init__(self, dash: bool = False, **kwargs) -> None: ...
    def output(self, key, obj, **kwargs): ...

class Polymorph(Nested):
    mapping: Incomplete
    def __init__(self, mapping, required: bool = False, **kwargs) -> None: ...
    def output(self, key, obj, ordered: bool = False, **kwargs): ...
    def resolve_ancestor(self, models): ...
    def clone(self, mask=None): ...

class Wildcard(Raw):
    exclude: Incomplete
    container: Incomplete
    def __init__(self, cls_or_instance, **kwargs) -> None: ...
    @property
    def key(self): ...
    def reset(self) -> None: ...
    def output(self, key, obj, ordered: bool = False): ...
    def schema(self): ...
    def clone(self): ...
