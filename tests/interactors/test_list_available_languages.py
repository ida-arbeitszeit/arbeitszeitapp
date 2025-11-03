from unittest import TestCase

from arbeitszeit.interactors.list_available_languages import (
    ListAvailableLanguagesInteractor,
)
from tests.interactors.repositories import FakeLanguageRepository

from .dependency_injection import get_dependency_injector


class InteractorTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.interactor = self.injector.get(ListAvailableLanguagesInteractor)
        self.language_repository = self.injector.get(FakeLanguageRepository)

    def test_with_no_languages_in_repository_no_codes_are_available(self) -> None:
        request = ListAvailableLanguagesInteractor.Request()
        response = self.interactor.list_available_languages(request)
        self.assertFalse(response.available_language_codes)

    def test_list_available_languages_if_one_exists(self) -> None:
        self.language_repository.add_language("de")
        request = ListAvailableLanguagesInteractor.Request()
        response = self.interactor.list_available_languages(request)
        self.assertTrue(response.available_language_codes)
