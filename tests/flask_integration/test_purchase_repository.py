from datetime import datetime
from unittest import TestCase

from arbeitszeit_flask.database.repositories import PurchaseRepository
from tests.data_generators import CompanyGenerator, MemberGenerator, PurchaseGenerator

from .dependency_injection import get_dependency_injector


class PurchaseRepoTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.repository = self.injector.get(PurchaseRepository)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_that_purchases_of_member_are_returned_in_correct_order(self) -> None:
        user = self.member_generator.create_member()
        earlier_purchase = self.purchase_generator.create_purchase(
            buyer=user, purchase_date=datetime(2000, 1, 1)
        )
        later_purchase = self.purchase_generator.create_purchase(
            buyer=user, purchase_date=datetime(2001, 2, 2)
        )
        result = list(self.repository.get_purchases_descending_by_date(user))
        assert [later_purchase, earlier_purchase] == result

    def test_that_list_of_purchases_of_company_contains_purchase_of_company(
        self,
    ):
        company = self.company_generator.create_company()
        purchase = self.purchase_generator.create_purchase(buyer=company)
        result = self.repository.get_purchases_of_company(company.id)
        self.assertIn(purchase, result)
