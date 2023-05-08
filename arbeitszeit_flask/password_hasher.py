from werkzeug.security import check_password_hash, generate_password_hash


class PasswordHasherImpl:
    def calculate_password_hash(self, password: str) -> str:
        return generate_password_hash(password, method="sha256")

    def is_password_matching_hash(self, password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, password)
