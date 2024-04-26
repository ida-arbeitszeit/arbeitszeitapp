from _typeshed import Incomplete

__all__ = ["Recaptcha"]

class Recaptcha:
    message: Incomplete
    def __init__(self, message: Incomplete | None = None) -> None: ...
    def __call__(self, form, field): ...
