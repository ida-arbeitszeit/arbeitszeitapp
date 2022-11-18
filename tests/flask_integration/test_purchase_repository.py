from datetime import datetime
from unittest import TestCase

from arbeitszeit_flask.database.repositories import PurchaseRepository
from tests.data_generators import CompanyGenerator, MemberGenerator, PurchaseGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class GetPurchasesTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.repository = self.injector.get(PurchaseRepository)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_a_purchase_shows_up_in_result(
        self,
    ):
        company = self.company_generator.create_company_entity()
        purchase = self.purchase_generator.create_purchase_by_company(buyer=company)
        result = list(self.repository.get_purchases())
        assert purchase in result

    def test_purchases_can_be_ordered_by_creation_date(
        self,
    ):
        self.datetime_service.freeze_time(datetime(2000, 1, 2))
        second_purchase = self.purchase_generator.create_purchase_by_company()
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        first_purchase = self.purchase_generator.create_purchase_by_company()
        result = list(self.repository.get_purchases().ordered_by_creation_date())
        assert first_purchase.purchase_date == result[0].purchase_date
        assert second_purchase.purchase_date == result[1].purchase_date

    def test_purchases_can_be_ordered_by_creation_date_descending(
        self,
    ):
        self.datetime_service.freeze_time(datetime(2000, 1, 2))
        second_purchase = self.purchase_generator.create_purchase_by_company()
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        first_purchase = self.purchase_generator.create_purchase_by_company()
        result = list(
            self.repository.get_purchases().ordered_by_creation_date(ascending=False)
        )
        assert first_purchase.purchase_date == result[1].purchase_date
        assert second_purchase.purchase_date == result[0].purchase_date

    def test_purchases_can_be_filtered_by_company(self) -> None:
        buyer = self.company_generator.create_company_entity()
        self.purchase_generator.create_purchase_by_company(buyer=buyer)
        self.purchase_generator.create_purchase_by_company()
        assert len(self.repository.get_purchases().conducted_by_company(buyer.id)) == 1

    def test_purchases_can_be_filtered_by_member(self) -> None:
        buyer = self.member_generator.create_member_entity()
        self.purchase_generator.create_purchase_by_member(buyer=buyer)
        self.purchase_generator.create_purchase_by_member()
        assert len(self.repository.get_purchases().conducted_by_member(buyer.id)) == 1
