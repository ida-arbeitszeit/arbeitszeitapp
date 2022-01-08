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

    def confirm_token(self, token: str) -> str:
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            original_string = serializer.loads(
                token,
                salt=current_app.config["SECURITY_PASSWORD_SALT"],
                max_age=3600,  # valid one hour
            )
        except Exception as exc:
            raise exc
        return original_string
