from _typeshed import Incomplete

from .core import Field

__all__ = [
    "BooleanField",
    "TextAreaField",
    "PasswordField",
    "FileField",
    "MultipleFileField",
    "HiddenField",
    "SearchField",
    "SubmitField",
    "StringField",
    "TelField",
    "URLField",
    "EmailField",
    "ColorField",
]

class BooleanField(Field):
    widget: Incomplete
    false_values: Incomplete
    def __init__(
        self, label=None, validators=None, false_values=None, **kwargs
    ) -> None: ...
    data: Incomplete
    def process_data(self, value) -> None: ...
    def process_formdata(self, valuelist) -> None: ...

class StringField(Field):
    widget: Incomplete
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class TextAreaField(StringField):
    widget: Incomplete

class PasswordField(StringField):
    widget: Incomplete

class FileField(Field):
    widget: Incomplete

class MultipleFileField(FileField):
    widget: Incomplete
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class HiddenField(StringField):
    widget: Incomplete

class SubmitField(BooleanField):
    widget: Incomplete

class SearchField(StringField):
    widget: Incomplete

class TelField(StringField):
    widget: Incomplete

class URLField(StringField):
    widget: Incomplete

class EmailField(StringField):
    widget: Incomplete

class ColorField(StringField):
    widget: Incomplete
