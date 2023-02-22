from datetime import datetime
from decimal import Decimal
from typing import List
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases.query_purchases import PurchaseQueryResponse
from arbeitszeit_web.presenters.member_purchases import MemberPurchasesPresenter
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import get_dependency_injector


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(MemberPurchasesPresenter)
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def test_that_date_is_formatted_properly(self) -> None:
        response = self.create_response_with_one_purchase(
            purchase_timestamp=datetime(2000, 1, 1)
        )
        view_model = self.presenter.present_member_purchases(response)
        self.assertEqual(
            view_model.purchases[0].purchase_date,
            self.datetime_service.format_datetime(
                datetime(2000, 1, 1),
                fmt="%d.%m.%Y",
            ),
        )

    def create_response_with_one_purchase(
        self, purchase_timestamp: datetime = datetime(2020, 1, 1)
    ) -> List[PurchaseQueryResponse]:
        return [
            PurchaseQueryResponse(
                purchase_date=purchase_timestamp,
                plan_id=uuid4(),
                product_name="test product",
                product_description="test product description",
                purpose=PurposesOfPurchases.consumption,
                price_per_unit=Decimal("1"),
                amount=1,
                price_total=Decimal("1"),
            )
        ]
