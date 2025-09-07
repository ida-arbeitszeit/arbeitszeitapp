from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.review_registered_consumptions import (
    RegisteredConsumption,
)
from arbeitszeit.use_cases.review_registered_consumptions import (
    ReviewRegisteredConsumptionsUseCase as UseCase,
)
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.www.presenters.review_registered_consumptions_presenter import (
    ReviewRegisteredConsumptionsPresenter,
)
from tests.datetime_service import datetime_utc
from tests.www.base_test_case import BaseTestCase


class ReviewRegisteredConsumptionsPresenterTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.presenter = self.injector.get(ReviewRegisteredConsumptionsPresenter)

    def test_that_an_use_case_response_without_consumptions_results_in_an_empty_view_model(
        self,
    ) -> None:
        use_case_response = UseCase.Response(consumptions=[])
        view_model = self.presenter.present(use_case_response)
        assert not view_model.consumptions

    def test_that_an_use_case_response_with_one_consumption_results_in_a_view_model_with_one_consumption(
        self,
    ) -> None:
        consumption = self._create_consumption()
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert len(view_model.consumptions) == 1

    def test_that_an_use_case_response_with_two_consumptions_results_in_a_view_model_with_two_consumptions(
        self,
    ) -> None:
        consumptions = [self._create_consumption(), self._create_consumption()]
        use_case_response = UseCase.Response(consumptions=consumptions)
        view_model = self.presenter.present(use_case_response)
        assert len(view_model.consumptions) == 2

    def test_if_there_is_a_use_case_response_with_two_consumptions_the_view_model_shows_correct_product_names(
        self,
    ) -> None:
        consumptions = [
            self._create_consumption(product_name="product 1"),
            self._create_consumption(product_name="product 2"),
        ]
        use_case_response = UseCase.Response(consumptions=consumptions)
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[0].product_name == "product 1"
        assert view_model.consumptions[1].product_name == "product 2"

    def test_that_an_use_case_response_results_in_a_view_model_with_a_formatted_consumption_date(
        self,
    ) -> None:
        date = datetime_utc(2021, 1, 1, 22, 1)
        consumption = self._create_consumption(date=date)
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[0].date == self.datetime_service.format_datetime(
            date=date, fmt="%d.%m.%Y %H:%M", zone="Europe/Berlin"
        )

    def test_that_an_use_case_response_results_in_a_view_model_with_the_consumer_name(
        self,
    ) -> None:
        expected_consumer_name = "consumer name"
        consumption = self._create_consumption(consumer_name=expected_consumer_name)
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[0].consumer_name == expected_consumer_name

    def test_that_the_view_model_has_no_consumer_url_if_the_consumption_is_private(
        self,
    ) -> None:
        consumption = self._create_consumption(is_private_consumption=True)
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[0].consumer_url is None

    def test_that_the_view_model_has_a_consumer_url_if_the_consumption_is_productive(
        self,
    ) -> None:
        consumption = self._create_consumption(is_private_consumption=False)
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[0].consumer_url is not None

    def test_that_the_view_model_has_a_consumer_url_if_the_consumption_is_productive_that_points_to_the_company_summary(
        self,
    ) -> None:
        expected_consumer_id = uuid4()
        consumption = self._create_consumption(
            is_private_consumption=False, consumer_id=expected_consumer_id
        )
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[
            0
        ].consumer_url == self.url_index.get_company_summary_url(expected_consumer_id)

    def test_that_the_view_model_has_a_private_consumer_type_icon_if_the_consumption_is_private(
        self,
    ) -> None:
        consumption = self._create_consumption(is_private_consumption=True)
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[0].consumer_type_icon == "user"

    def test_that_the_view_model_has_a_productive_consumer_type_icon_if_the_consumption_is_productive(
        self,
    ) -> None:
        consumption = self._create_consumption(is_private_consumption=False)
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[0].consumer_type_icon == "industry"

    def test_that_an_use_case_response_results_in_a_view_model_with_the_product_name(
        self,
    ) -> None:
        expected_product_name = "product name"
        consumption = self._create_consumption(product_name=expected_product_name)
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[0].product_name == expected_product_name

    def test_that_an_use_case_response_results_in_a_view_model_with_a_plan_url(
        self,
    ) -> None:
        consumption = self._create_consumption()
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[
            0
        ].plan_url == self.url_index.get_plan_details_url(
            plan_id=consumption.plan_id, user_role=UserRole.company
        )

    def test_that_an_use_case_response_results_in_a_view_model_with_formatted_labour_hours_consumed(
        self,
    ) -> None:
        consumption = self._create_consumption(labour_hours_consumed=Decimal(10.007))
        use_case_response = UseCase.Response(consumptions=[consumption])
        view_model = self.presenter.present(use_case_response)
        assert view_model.consumptions[0].labour_hours_consumed == "10.01"

    def _create_consumption(
        self,
        date: datetime = datetime_utc(2021, 1, 1),
        is_private_consumption: Optional[bool] = None,
        consumer_name: str = "consumer_name",
        consumer_id: UUID = uuid4(),
        product_name: str = "product_name",
        plan_id: UUID = uuid4(),
        labour_hours_consumed: Decimal = Decimal(10.007),
    ) -> RegisteredConsumption:
        if is_private_consumption is None:
            is_private_consumption = False
        return RegisteredConsumption(
            date=date,
            is_private_consumption=is_private_consumption,
            consumer_name=consumer_name,
            consumer_id=consumer_id,
            product_name=product_name,
            plan_id=plan_id,
            labour_hours_consumed=labour_hours_consumed,
        )
