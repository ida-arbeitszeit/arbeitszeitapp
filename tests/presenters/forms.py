from __future__ import annotations

from typing import Generic, List, TypeVar

T = TypeVar("T")


class LoginForm:
    def __init__(self) -> None:
        self.email_errors: List[str] = []
        self.password_errors: List[str] = []
        self._is_remember: bool = False

    def email_field(self) -> FormFieldImpl[str]:
        return FormFieldImpl(value="test value", errors=self.email_errors)

    def password_field(self) -> FormFieldImpl[str]:
        return FormFieldImpl(value="test password", errors=self.password_errors)

    def remember_field(self) -> FormFieldImpl[bool]:
        return FormFieldImpl(value=self._is_remember, errors=[])

    def has_errors(self) -> bool:
        return bool(self.email_errors or self.password_errors)

    def set_remember_field(self, state: bool) -> None:
        self._is_remember = state


class FormFieldImpl(Generic[T]):
    def __init__(self, value: T, errors: List[str]) -> None:
        self.errors = errors
        self.value = value

    def get_value(self) -> T:
        return self.value

    def attach_error(self, message: str) -> None:
        self.errors.append(message)
