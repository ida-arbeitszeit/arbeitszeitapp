from werkzeug.security import check_password_hash, generate_password_hash


class PasswordHasherImpl:
    def calculate_password_hash(self, password: str) -> str:
        return generate_password_hash(password)

    def is_password_matching_hash(self, password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, password)

    def is_regeneration_needed(self, password_hash: str) -> bool:
        try:
            method, _ = password_hash.split("$", maxsplit=1)
        except ValueError:
            return True
        return method == "sha256"
