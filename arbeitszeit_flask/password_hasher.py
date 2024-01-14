import importlib

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from arbeitszeit.injector import Injector
from arbeitszeit.password_hasher import PasswordHasher


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


def provide_password_hasher(injector: Injector) -> PasswordHasher:
    config = current_app.config["ARBEITSZEIT_PASSWORD_HASHER"]
    module_name, klass_name = config.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    klass = getattr(module, klass_name)
    return injector.get(klass)
