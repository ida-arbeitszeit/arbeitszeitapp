from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.repositories import LanguageRepository


@dataclass
class ListAvailableLanguagesInteractor:
    class Request:
        pass

    @dataclass
    class Response:
        available_language_codes: List[str]

    language_repository: LanguageRepository

    def list_available_languages(self, request: Request) -> Response:
        return self.Response(
            available_language_codes=list(
                self.language_repository.get_available_language_codes()
            )
        )
