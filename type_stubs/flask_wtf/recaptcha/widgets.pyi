from _typeshed import Incomplete

__all__ = ["RecaptchaWidget"]

class RecaptchaWidget:
    def recaptcha_html(self, public_key): ...
    def __call__(self, field, error: Incomplete | None = None, **kwargs): ...
