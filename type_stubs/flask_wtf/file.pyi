from _typeshed import Incomplete
from wtforms import FileField as _FileField
from wtforms import MultipleFileField as _MultipleFileField
from wtforms.validators import DataRequired

class FileField(_FileField):
    data: Incomplete
    raw_data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class MultipleFileField(_MultipleFileField):
    data: Incomplete
    raw_data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class FileRequired(DataRequired):
    def __call__(self, form, field) -> None: ...

file_required = FileRequired

class FileAllowed:
    upload_set: Incomplete
    message: Incomplete
    def __init__(self, upload_set, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...

file_allowed = FileAllowed

class FileSize:
    min_size: Incomplete
    max_size: Incomplete
    message: Incomplete
    def __init__(self, max_size, min_size: int = 0, message=None) -> None: ...
    def __call__(self, form, field) -> None: ...

file_size = FileSize
