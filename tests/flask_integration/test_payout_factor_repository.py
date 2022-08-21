from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.repositories import PayoutFactorRepository
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class PayoutFactorRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.repository = self.injector.get(PayoutFactorRepository)

    def test_can_store_and_retrieve_payout_factor(self):
        payout_factor = Decimal("-1.1")
        self.repository.store_payout_factor(self.datetime_service.now(), payout_factor)
        retrieved_payout_factor = self.repository.get_latest_payout_factor()
        assert payout_factor == retrieved_payout_factor.value

    def test_return_none_when_no_payout_factor_is_stored_in_database(self):
        result = self.repository.get_latest_payout_factor()
        assert result is None

    def test_latest_payout_factor_is_retrieved(self):
        expected_payout_factor = Decimal("10")
        self.datetime_service.freeze_time(datetime(2020, 1, 1, 10))
        self.repository.store_payout_factor(self.datetime_service.now(), Decimal("5"))
        self.datetime_service.freeze_time(datetime(2020, 3, 1, 10))
        self.repository.store_payout_factor(
            self.datetime_service.now(), expected_payout_factor
        )
        self.datetime_service.freeze_time(datetime(2020, 2, 1, 10))
        self.repository.store_payout_factor(self.datetime_service.now(), Decimal("15"))
        payout_factor = self.repository.get_latest_payout_factor()
        assert payout_factor.value == expected_payout_factor
        assert payout_factor.timestamp == datetime(2020, 3, 1, 10)
