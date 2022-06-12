from unittest import TestCase

from arbeitszeit.use_cases.list_available_languages import ListAvailableLanguagesUseCase
from tests.use_cases.repositories import FakeLanguageRepository

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ListAvailableLanguagesUseCase)
        self.language_repository = self.injector.get(FakeLanguageRepository)

    def test_with_no_languages_in_repository_no_codes_are_available(self) -> None:
        request = ListAvailableLanguagesUseCase.Request()
        response = self.use_case.list_available_languages(request)
        self.assertFalse(response.available_language_codes)

    def test_list_available_languages_if_one_exists(self) -> None:
        self.language_repository.add_language("de")
        request = ListAvailableLanguagesUseCase.Request()
        response = self.use_case.list_available_languages(request)
        self.assertTrue(response.available_language_codes)
