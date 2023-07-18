from unittest import TestCase

from .dependency_injection import get_dependency_injector


class BaseTestCase(TestCase):
    "Presenter unit tests should inherit from this class."

    def setUp(self) -> None:
        self.injector = get_dependency_injector()
