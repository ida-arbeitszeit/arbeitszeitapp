from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.use_cases import query_private_consumptions as use_case
from arbeitszeit_web.www.presenters.private_consumptions_presenter import (
    PrivateConsumptionsPresenter,
)
from tests.datetime_service import datetime_utc
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(PrivateConsumptionsPresenter)

    def test_that_date_is_formatted_properly(self) -> None:
        response = self.create_response_with_one_consumption(
            consumption_timestamp=datetime_utc(2000, 1, 1)
        )
        view_model = self.presenter.present_private_consumptions(response)
        self.assertEqual(
            view_model.consumptions[0].consumption_date,
            self.datetime_service.format_datetime(
                datetime_utc(2000, 1, 1),
                fmt="%d.%m.%Y",
            ),
        )

    def create_response_with_one_consumption(
        self, consumption_timestamp: datetime = datetime_utc(2020, 1, 1)
    ) -> use_case.Response:
        return use_case.Response(
            consumptions=[
                use_case.Consumption(
                    consumption_date=consumption_timestamp,
                    plan_id=uuid4(),
                    product_name="test product",
                    product_description="test product description",
                    price_per_unit=Decimal("1"),
                    amount=1,
                    price_total=Decimal("1"),
                )
            ]
        )
