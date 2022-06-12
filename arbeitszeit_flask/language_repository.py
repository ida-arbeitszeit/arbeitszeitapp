from typing import Iterable, Optional

from flask import current_app


class LanguageRepositoryImpl:
    def get_available_language_codes(self) -> Iterable[str]:
        language_config = current_app.config["LANGUAGES"]
        return language_config.keys()

    def get_language_name(self, code: str) -> Optional[str]:
        return current_app.config["LANGUAGES"].get(code)
