from typing import Optional, Protocol


class LanguageService(Protocol):
    def get_language_name(self, code: str) -> Optional[str]: ...
