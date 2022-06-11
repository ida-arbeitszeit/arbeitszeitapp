from unittest import TestCase

from arbeitszeit.use_cases.select_preferred_language import (
    SelectPreferredLanguageUseCase,
)

from .dependency_injection import get_dependency_injector


class SelectLanguageTest(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(SelectPreferredLanguageUseCase)

    def test(self) -> None:
        pass
