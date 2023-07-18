from unittest import TestCase

from .dependency_injection import get_dependency_injector


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector()
