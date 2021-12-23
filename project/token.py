from itsdangerous import URLSafeTimedSerializer


def generate_confirmation_token(email, secret_key, salt):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt=salt)


def confirm_token(token, secret_key, salt, expiration=3600):  # valid one hour
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(token, salt=salt, max_age=expiration)
    except Exception as exc:
        raise exc
    return email
