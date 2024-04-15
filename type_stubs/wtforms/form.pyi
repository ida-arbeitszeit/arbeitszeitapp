from _typeshed import Incomplete
from wtforms.meta import DefaultMeta

__all__ = ["BaseForm", "Form"]

class BaseForm:
    meta: Incomplete
    form_errors: Incomplete
    def __init__(self, fields, prefix: str = "", meta=...) -> None: ...
    def __iter__(self): ...
    def __contains__(self, name) -> bool: ...
    def __getitem__(self, name): ...
    def __setitem__(self, name, value) -> None: ...
    def __delitem__(self, name) -> None: ...
    def populate_obj(self, obj) -> None: ...
    def process(
        self,
        formdata: Incomplete | None = None,
        obj: Incomplete | None = None,
        data: Incomplete | None = None,
        extra_filters: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def validate(self, extra_validators: Incomplete | None = None): ...
    @property
    def data(self): ...
    @property
    def errors(self): ...

class FormMeta(type):
    def __init__(cls, name, bases, attrs) -> None: ...
    def __call__(cls, *args, **kwargs): ...
    def __setattr__(cls, name, value) -> None: ...
    def __delattr__(cls, name) -> None: ...

class Form(BaseForm, metaclass=FormMeta):
    Meta = DefaultMeta
    def __init__(
        self,
        formdata: Incomplete | None = None,
        obj: Incomplete | None = None,
        prefix: str = "",
        data: Incomplete | None = None,
        meta: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def __setitem__(self, name, value) -> None: ...
    def __delitem__(self, name) -> None: ...
    def __delattr__(self, name) -> None: ...
    def validate(self, extra_validators: Incomplete | None = None): ...
