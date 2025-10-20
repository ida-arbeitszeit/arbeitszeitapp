from typing import Any, Dict
from unittest import TestCase

from tests.data_generators import AccountantGenerator, CompanyGenerator, MemberGenerator
from tests.datetime_service import FakeDatetimeService
from tests.email import FakeEmailService
from tests.lazy_property import _lazy_property
from tests.request import FakeRequest
from tests.session import FakeSession
from tests.token import FakeTokenService
from tests.translator import FakeTranslator
from tests.www.datetime_formatter import (
    FakeDatetimeFormatter,
    FakeTimezoneConfiguration,
)
from tests.www.presenters.notifier import NotifierTestImpl
from tests.www.presenters.url_index import UrlIndexTestImpl

from .dependency_injection import get_dependency_injector


class BaseTestCase(TestCase):
    "Wwww unit tests should inherit from this class."

    def setUp(self) -> None:
        super().setUp()
        self._lazy_property_cache: Dict[str, Any] = dict()
        self.injector = get_dependency_injector()

    def tearDown(self) -> None:
        self._lazy_property_cache = dict()
        super().tearDown()

    # It would be nice to have the following list sorted
    # alphabetically
    accountant_generator = _lazy_property(AccountantGenerator)
    company_generator = _lazy_property(CompanyGenerator)
    datetime_service = _lazy_property(FakeDatetimeService)
    datetime_formatter = _lazy_property(FakeDatetimeFormatter)
    timezone_configuration = _lazy_property(FakeTimezoneConfiguration)
    email_service = _lazy_property(FakeEmailService)
    member_generator = _lazy_property(MemberGenerator)
    notifier = _lazy_property(NotifierTestImpl)
    request = _lazy_property(FakeRequest)
    session = _lazy_property(FakeSession)
    token_service = _lazy_property(FakeTokenService)
    translator = _lazy_property(FakeTranslator)
    url_index = _lazy_property(UrlIndexTestImpl)
