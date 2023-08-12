from _typeshed import Incomplete
from wtforms import i18n as i18n
from wtforms.utils import WebobInputWrapper as WebobInputWrapper
from wtforms.widgets.core import clean_key as clean_key

class DefaultMeta:
    def bind_field(self, form, unbound_field, options): ...
    def wrap_formdata(self, form, formdata): ...
    def render_field(self, field, render_kw): ...
    csrf: bool
    csrf_field_name: str
    csrf_secret: Incomplete
    csrf_context: Incomplete
    csrf_class: Incomplete
    def build_csrf(self, form): ...
    locales: bool
    cache_translations: bool
    translations_cache: Incomplete
    def get_translations(self, form): ...
    def update_values(self, values) -> None: ...
