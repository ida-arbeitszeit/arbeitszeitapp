class PasswordHasherImpl:
    def calculate_password_hash(self, password: str) -> str:
        return "123-" + password

    def is_password_matching_hash(self, password: str, password_hash: str) -> bool:
        return password == password_hash[4:]

    def is_regeneration_needed(self, password_hash: str) -> bool:
        return False
