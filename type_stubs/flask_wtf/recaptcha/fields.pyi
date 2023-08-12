from _typeshed import Incomplete
from wtforms.fields import Field

class RecaptchaField(Field):
    widget: Incomplete
    recaptcha_error: Incomplete
    def __init__(self, label: str = ..., validators: Incomplete | None = ..., **kwargs) -> None: ...
