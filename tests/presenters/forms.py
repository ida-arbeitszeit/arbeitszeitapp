from typing import List


class LoginForm:
    def __init__(self) -> None:
        self.email_errors: List[str] = []
        self.password_errors: List[str] = []
        self._is_remember: bool = False

    def add_email_error(self, error: str) -> None:
        self.email_errors.append(error)

    def add_password_error(self, error: str) -> None:
        self.password_errors.append(error)

    def has_errors(self) -> bool:
        return bool(self.email_errors or self.password_errors)

    def set_remember_field(self, state: bool) -> None:
        self._is_remember = state

    def get_remember_field(self) -> bool:
        return self._is_remember
