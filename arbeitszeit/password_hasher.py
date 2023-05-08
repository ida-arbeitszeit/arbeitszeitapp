from typing import Protocol


class PasswordHasher(Protocol):
    def calculate_password_hash(self, password: str) -> str:
        ...

    def is_password_matching_hash(self, password: str, password_hash: str) -> bool:
        ...
