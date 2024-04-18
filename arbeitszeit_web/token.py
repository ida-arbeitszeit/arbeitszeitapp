from datetime import timedelta
from typing import Optional, Protocol


class TokenService(Protocol):
    def generate_token(self, input: str) -> str: ...

    def confirm_token(self, token: str, max_age: timedelta) -> Optional[str]: ...
