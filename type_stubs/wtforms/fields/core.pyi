from _typeshed import Incomplete
from wtforms import widgets as widgets
from wtforms.i18n import DummyTranslations as DummyTranslations
from wtforms.utils import unset_value as unset_value
from wtforms.validators import StopValidation as StopValidation
from wtforms.validators import ValidationError as ValidationError

class Field:
    errors: Incomplete
    process_errors: Incomplete
    raw_data: Incomplete
    validators: Incomplete
    widget: Incomplete
    do_not_call_in_templates: bool
    def __new__(cls, *args, **kwargs): ...
    meta: Incomplete
    default: Incomplete
    description: Incomplete
    render_kw: Incomplete
    filters: Incomplete
    flags: Incomplete
    name: Incomplete
    short_name: Incomplete
    type: Incomplete
    id: Incomplete
    label: Incomplete
    def __init__(
        self,
        label: Incomplete | None = None,
        validators: Incomplete | None = None,
        filters=(),
        description: str = "",
        id: Incomplete | None = None,
        default: Incomplete | None = None,
        widget: Incomplete | None = None,
        render_kw: Incomplete | None = None,
        name: Incomplete | None = None,
        _form: Incomplete | None = None,
        _prefix: str = "",
        _translations: Incomplete | None = None,
        _meta: Incomplete | None = None,
    ) -> None: ...
    def __html__(self): ...
    def __call__(self, **kwargs): ...
    @classmethod
    def check_validators(cls, validators) -> None: ...
    def gettext(self, string): ...
    def ngettext(self, singular, plural, n): ...
    def validate(self, form, extra_validators=()): ...
    def pre_validate(self, form) -> None: ...
    def post_validate(self, form, validation_stopped) -> None: ...
    object_data: Incomplete
    data: Incomplete
    def process(
        self, formdata, data=..., extra_filters: Incomplete | None = None
    ) -> None: ...
    def process_data(self, value) -> None: ...
    def process_formdata(self, valuelist) -> None: ...
    def populate_obj(self, obj, name) -> None: ...

class UnboundField:
    creation_counter: int
    field_class: Incomplete
    args: Incomplete
    name: Incomplete
    kwargs: Incomplete
    def __init__(
        self, field_class, *args, name: Incomplete | None = None, **kwargs
    ) -> None: ...
    def bind(
        self,
        form,
        name,
        prefix: str = "",
        translations: Incomplete | None = None,
        **kwargs,
    ): ...

class Flags:
    def __getattr__(self, name): ...
    def __contains__(self, name) -> bool: ...

class Label:
    field_id: Incomplete
    text: Incomplete
    def __init__(self, field_id, text) -> None: ...
    def __html__(self): ...
    def __call__(self, text: Incomplete | None = None, **kwargs): ...
