from typing import Optional

from flask import current_app
from injector import singleton
from itsdangerous import URLSafeTimedSerializer


@singleton
class FlaskTokenService:
    def generate_token(self, input: str) -> str:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = serializer.dumps(
            input, salt=current_app.config["SECURITY_PASSWORD_SALT"]
        )
        assert isinstance(token, str)
        return token

    def confirm_token(self, token: str, max_age_in_sec: int = 3600) -> Optional[str]:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        original_string = serializer.loads(
            token,
            salt=current_app.config["SECURITY_PASSWORD_SALT"],
            max_age=max_age_in_sec,  # valid 3600 sec = one hour
        )
        return original_string
