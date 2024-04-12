from _typeshed import Incomplete
from werkzeug.exceptions import BadRequest
from wtforms.csrf.core import CSRF

__all__ = ["generate_csrf", "validate_csrf", "CSRFProtect"]

def generate_csrf(
    secret_key: Incomplete | None = None, token_key: Incomplete | None = None
): ...
def validate_csrf(
    data,
    secret_key: Incomplete | None = None,
    time_limit: Incomplete | None = None,
    token_key: Incomplete | None = None,
) -> None: ...

class _FlaskFormCSRF(CSRF):
    meta: Incomplete
    def setup_form(self, form): ...
    def generate_csrf_token(self, csrf_token_field): ...
    def validate_csrf_token(self, form, field) -> None: ...

class CSRFProtect:
    def __init__(self, app: Incomplete | None = None) -> None: ...
    def init_app(self, app): ...
    def protect(self) -> None: ...
    def exempt(self, view): ...

class CSRFError(BadRequest):
    description: str
