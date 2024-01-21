from _typeshed import Incomplete

class ValidationError(ValueError):
    def __init__(self, message: str = ..., *args, **kwargs) -> None: ...

class StopValidation(Exception):
    def __init__(self, message: str = ..., *args, **kwargs) -> None: ...

class EqualTo:
    fieldname: Incomplete
    message: Incomplete
    def __init__(self, fieldname, message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class Length:
    min: Incomplete
    max: Incomplete
    message: Incomplete
    field_flags: Incomplete
    def __init__(self, min: int = ..., max: int = ..., message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class NumberRange:
    min: Incomplete
    max: Incomplete
    message: Incomplete
    field_flags: Incomplete
    def __init__(self, min: Incomplete | None = ..., max: Incomplete | None = ..., message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class Optional:
    string_check: Incomplete
    field_flags: Incomplete
    def __init__(self, strip_whitespace: bool = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class DataRequired:
    message: Incomplete
    field_flags: Incomplete
    def __init__(self, message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class InputRequired:
    message: Incomplete
    field_flags: Incomplete
    def __init__(self, message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class Regexp:
    regex: Incomplete
    message: Incomplete
    def __init__(self, regex, flags: int = ..., message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field, message: Incomplete | None = ...): ...

class Email:
    message: Incomplete
    granular_message: Incomplete
    check_deliverability: Incomplete
    allow_smtputf8: Incomplete
    allow_empty_local: Incomplete
    def __init__(self, message: Incomplete | None = ..., granular_message: bool = ..., check_deliverability: bool = ..., allow_smtputf8: bool = ..., allow_empty_local: bool = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class IPAddress:
    ipv4: Incomplete
    ipv6: Incomplete
    message: Incomplete
    def __init__(self, ipv4: bool = ..., ipv6: bool = ..., message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...
    @classmethod
    def check_ipv4(cls, value): ...
    @classmethod
    def check_ipv6(cls, value): ...

class MacAddress(Regexp):
    def __init__(self, message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class URL(Regexp):
    validate_hostname: Incomplete
    def __init__(self, require_tld: bool = ..., allow_ip: bool = ..., message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class UUID:
    message: Incomplete
    def __init__(self, message: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...

class AnyOf:
    values: Incomplete
    message: Incomplete
    values_formatter: Incomplete
    def __init__(self, values, message: Incomplete | None = ..., values_formatter: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...
    @staticmethod
    def default_values_formatter(values): ...

class NoneOf:
    values: Incomplete
    message: Incomplete
    values_formatter: Incomplete
    def __init__(self, values, message: Incomplete | None = ..., values_formatter: Incomplete | None = ...) -> None: ...
    def __call__(self, form, field) -> None: ...
    @staticmethod
    def default_values_formatter(v): ...

class HostnameValidation:
    hostname_part: Incomplete
    tld_part: Incomplete
    require_tld: Incomplete
    allow_ip: Incomplete
    def __init__(self, require_tld: bool = ..., allow_ip: bool = ...) -> None: ...
    def __call__(self, hostname): ...

class ReadOnly:
    field_flags: Incomplete
    def __init__(self) -> None: ...
    def __call__(self, form, field) -> None: ...

class Disabled:
    field_flags: Incomplete
    def __init__(self) -> None: ...
    def __call__(self, form, field) -> None: ...
email = Email
equal_to = EqualTo
ip_address = IPAddress
mac_address = MacAddress
length = Length
number_range = NumberRange
optional = Optional
input_required = InputRequired
data_required = DataRequired
regexp = Regexp
url = URL
any_of = AnyOf
none_of = NoneOf
readonly = ReadOnly
disabled = Disabled
