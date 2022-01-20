from flask import current_app
from injector import singleton
from itsdangerous import URLSafeTimedSerializer


@singleton
class FlaskTokenService:
    def generate_token(self, input: str) -> str:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps(
            input, salt=current_app.config["SECURITY_PASSWORD_SALT"]
        )

    def confirm_token(self, token: str, max_age_in_sec: int = 3600) -> str:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            original_string = serializer.loads(
                token,
                salt=current_app.config["SECURITY_PASSWORD_SALT"],
                max_age=max_age_in_sec,  # valid 3600 sec = one hour
            )
        except Exception as exc:
            raise exc
        return original_string
