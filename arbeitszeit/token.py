from typing import Protocol


class TokenService(Protocol):
    def generate_token(self, input: str) -> str:
        ...

    def confirm_token(self, token: str, max_age_in_sec: int) -> str:
        ...
