from _typeshed import Incomplete

__all__ = [
    "CheckboxInput",
    "ColorInput",
    "DateInput",
    "DateTimeInput",
    "DateTimeLocalInput",
    "EmailInput",
    "FileInput",
    "HiddenInput",
    "ListWidget",
    "MonthInput",
    "NumberInput",
    "Option",
    "PasswordInput",
    "RadioInput",
    "RangeInput",
    "SearchInput",
    "Select",
    "SubmitInput",
    "TableWidget",
    "TextArea",
    "TextInput",
    "TelInput",
    "TimeInput",
    "URLInput",
    "WeekInput",
]

class ListWidget:
    html_tag: Incomplete
    prefix_label: Incomplete
    def __init__(self, html_tag: str = "ul", prefix_label: bool = True) -> None: ...
    def __call__(self, field, **kwargs): ...

class TableWidget:
    with_table_tag: Incomplete
    def __init__(self, with_table_tag: bool = True) -> None: ...
    def __call__(self, field, **kwargs): ...

class Input:
    html_params: Incomplete
    input_type: Incomplete
    def __init__(self, input_type=None) -> None: ...
    def __call__(self, field, **kwargs): ...

class TextInput(Input):
    input_type: str
    validation_attrs: Incomplete

class PasswordInput(Input):
    input_type: str
    validation_attrs: Incomplete
    hide_value: Incomplete
    def __init__(self, hide_value: bool = True) -> None: ...
    def __call__(self, field, **kwargs): ...

class HiddenInput(Input):
    input_type: str
    validation_attrs: Incomplete
    field_flags: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class CheckboxInput(Input):
    input_type: str
    validation_attrs: Incomplete
    def __call__(self, field, **kwargs): ...

class RadioInput(Input):
    input_type: str
    validation_attrs: Incomplete
    def __call__(self, field, **kwargs): ...

class FileInput(Input):
    input_type: str
    validation_attrs: Incomplete
    multiple: Incomplete
    def __init__(self, multiple: bool = False) -> None: ...
    def __call__(self, field, **kwargs): ...

class SubmitInput(Input):
    input_type: str
    validation_attrs: Incomplete
    def __call__(self, field, **kwargs): ...

class TextArea:
    validation_attrs: Incomplete
    def __call__(self, field, **kwargs): ...

class Select:
    validation_attrs: Incomplete
    multiple: Incomplete
    def __init__(self, multiple: bool = False) -> None: ...
    def __call__(self, field, **kwargs): ...
    @classmethod
    def render_option(cls, value, label, selected, **kwargs): ...

class Option:
    def __call__(self, field, **kwargs): ...

class SearchInput(Input):
    input_type: str
    validation_attrs: Incomplete

class TelInput(Input):
    input_type: str
    validation_attrs: Incomplete

class URLInput(Input):
    input_type: str
    validation_attrs: Incomplete

class EmailInput(Input):
    input_type: str
    validation_attrs: Incomplete

class DateTimeInput(Input):
    input_type: str
    validation_attrs: Incomplete

class DateInput(Input):
    input_type: str
    validation_attrs: Incomplete

class MonthInput(Input):
    input_type: str
    validation_attrs: Incomplete

class WeekInput(Input):
    input_type: str
    validation_attrs: Incomplete

class TimeInput(Input):
    input_type: str
    validation_attrs: Incomplete

class DateTimeLocalInput(Input):
    input_type: str
    validation_attrs: Incomplete

class NumberInput(Input):
    input_type: str
    validation_attrs: Incomplete
    step: Incomplete
    min: Incomplete
    max: Incomplete
    def __init__(self, step=None, min=None, max=None) -> None: ...
    def __call__(self, field, **kwargs): ...

class RangeInput(Input):
    input_type: str
    validation_attrs: Incomplete
    step: Incomplete
    def __init__(self, step=None) -> None: ...
    def __call__(self, field, **kwargs): ...

class ColorInput(Input):
    input_type: str
    validation_attrs: Incomplete
