from _typeshed import Incomplete

__all__ = [
    "DataRequired",
    "data_required",
    "Email",
    "email",
    "EqualTo",
    "equal_to",
    "IPAddress",
    "ip_address",
    "InputRequired",
    "input_required",
    "Length",
    "length",
    "NumberRange",
    "number_range",
    "Optional",
    "optional",
    "Regexp",
    "regexp",
    "URL",
    "url",
    "AnyOf",
    "any_of",
    "NoneOf",
    "none_of",
    "MacAddress",
    "mac_address",
    "UUID",
    "ValidationError",
    "StopValidation",
    "readonly",
    "ReadOnly",
    "disabled",
    "Disabled",
]

class ValidationError(ValueError):
    def __init__(self, message: str = "", *args, **kwargs) -> None: ...

class StopValidation(Exception):
    def __init__(self, message: str = "", *args, **kwargs) -> None: ...

class EqualTo:
    fieldname: Incomplete
    message: Incomplete
    def __init__(self, fieldname, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...

class Length:
    min: Incomplete
    max: Incomplete
    message: Incomplete
    field_flags: Incomplete
    def __init__(self, min: int = -1, max: int = -1, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...

class NumberRange:
    min: Incomplete
    max: Incomplete
    message: Incomplete
    field_flags: Incomplete
    def __init__(self, min=None, max=None, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...

class Optional:
    string_check: Incomplete
    field_flags: Incomplete
    def __init__(self, strip_whitespace: bool = True) -> None: ...
    def __call__(self, form, field) -> None: ...

class DataRequired:
    message: Incomplete
    field_flags: Incomplete
    def __init__(self, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...

class InputRequired:
    message: Incomplete
    field_flags: Incomplete
    def __init__(self, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...

class Regexp:
    regex: Incomplete
    message: Incomplete
    def __init__(self, regex, flags: int = 0, message=None) -> None: ...
    def __call__(self, form, field, message=None): ...

class Email:
    message: Incomplete
    granular_message: Incomplete
    check_deliverability: Incomplete
    allow_smtputf8: Incomplete
    allow_empty_local: Incomplete
    def __init__(
        self,
        message=None,
        granular_message: bool = False,
        check_deliverability: bool = False,
        allow_smtputf8: bool = True,
        allow_empty_local: bool = False,
    ) -> None: ...
    def __call__(self, form, field) -> None: ...

class IPAddress:
    ipv4: Incomplete
    ipv6: Incomplete
    message: Incomplete
    def __init__(self, ipv4: bool = True, ipv6: bool = False, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...
    @classmethod
    def check_ipv4(cls, value): ...
    @classmethod
    def check_ipv6(cls, value): ...

class MacAddress(Regexp):
    def __init__(self, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...

class URL(Regexp):
    validate_hostname: Incomplete
    def __init__(
        self, require_tld: bool = True, allow_ip: bool = True, message=None
    ) -> None: ...
    def __call__(self, form, field) -> None: ...

class UUID:
    message: Incomplete
    def __init__(self, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...

class AnyOf:
    values: Incomplete
    message: Incomplete
    values_formatter: Incomplete
    def __init__(self, values, message=None, values_formatter=None) -> None: ...
    def __call__(self, form, field) -> None: ...
    @staticmethod
    def default_values_formatter(values): ...

class NoneOf:
    values: Incomplete
    message: Incomplete
    values_formatter: Incomplete
    def __init__(self, values, message=None, values_formatter=None) -> None: ...
    def __call__(self, form, field) -> None: ...
    @staticmethod
    def default_values_formatter(v): ...

class HostnameValidation:
    hostname_part: Incomplete
    tld_part: Incomplete
    require_tld: Incomplete
    allow_ip: Incomplete
    def __init__(self, require_tld: bool = True, allow_ip: bool = False) -> None: ...
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
