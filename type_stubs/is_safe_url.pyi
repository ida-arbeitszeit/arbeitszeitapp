from _typeshed import Incomplete

PY2: Incomplete

class CustomUnicodeDecodeError(UnicodeDecodeError):
    obj: Incomplete
    def __init__(self, obj, *args) -> None: ...

def force_text(s): ...
def is_safe_url(url, allowed_hosts, require_https: bool = ...): ...
