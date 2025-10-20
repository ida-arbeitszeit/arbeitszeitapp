from unittest import TestCase

from arbeitszeit.injector import Injector
from tests.api.dependency_injection import ApiModule


class BaseTestCase(TestCase):
    "Presenter unit tests should inherit from this class."

    def setUp(self) -> None:
        super().setUp()
        self.injector = Injector([ApiModule()])
