from datetime import timedelta
from typing import Optional

from flask import current_app
from itsdangerous import BadSignature, URLSafeTimedSerializer

from arbeitszeit.injector import singleton


@singleton
class FlaskTokenService:
    def __init__(self) -> None:
        self.serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    def generate_token(self, input: str) -> str:
        token = self.serializer.dumps(
            input, salt=current_app.config["SECURITY_PASSWORD_SALT"]
        )
        assert isinstance(token, str)
        return token

    def confirm_token(self, token: str, max_age: timedelta) -> Optional[str]:
        try:
            return self._load_token(
                token, max_age_in_seconds=int(max_age.total_seconds())
            )
        except BadSignature:
            return None

    def _load_token(
        self, token: str, max_age_in_seconds: Optional[int] = None
    ) -> Optional[str]:
        return self.serializer.loads(
            token,
            salt=current_app.config["SECURITY_PASSWORD_SALT"],
            max_age=max_age_in_seconds,
        )
