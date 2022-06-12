from typing import Dict, Optional


class FakeLanguageService:
    def __init__(self) -> None:
        self._names: Dict[str, str] = dict()

    def get_language_name(self, code: str) -> Optional[str]:
        return self._names.get(code)

    def set_language_name(self, code: str, name: Optional[str]) -> None:
        if name is None:
            try:
                del self._names[code]
            except KeyError:
                pass
        else:
            self._names[code] = name
