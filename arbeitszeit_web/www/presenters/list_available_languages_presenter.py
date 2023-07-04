from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.list_available_languages import ListAvailableLanguagesUseCase
from arbeitszeit_web.language_service import LanguageService
from arbeitszeit_web.url_index import LanguageChangerUrlIndex


@dataclass
class ListAvailableLanguagesPresenter:
    @dataclass
    class LanguageListItem:
        change_url: str
        label: str

    @dataclass
    class ViewModel:
        show_language_listing: bool
        languages_listing: List[ListAvailableLanguagesPresenter.LanguageListItem]

    language_changer_url_index: LanguageChangerUrlIndex
    language_service: LanguageService

    def present_available_languages_list(
        self, response: ListAvailableLanguagesUseCase.Response
    ) -> ViewModel:
        return self.ViewModel(
            show_language_listing=bool(response.available_language_codes),
            languages_listing=[
                self.LanguageListItem(
                    change_url=self.language_changer_url_index.get_language_change_url(
                        code
                    ),
                    label=self.language_service.get_language_name(code) or code,
                )
                for code in response.available_language_codes
            ],
        )
