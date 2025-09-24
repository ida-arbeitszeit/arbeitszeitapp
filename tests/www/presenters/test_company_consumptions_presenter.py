from decimal import Decimal
from typing import Iterator
from uuid import uuid4

from arbeitszeit.interactors.query_company_consumptions import (
    ConsumptionQueryResponse,
    QueryCompanyConsumptionsInteractor,
)
from arbeitszeit.records import ConsumptionType
from arbeitszeit_web.www.presenters.company_consumptions_presenter import (
    CompanyConsumptionsPresenter,
    ViewModel,
)
from tests.data_generators import ConsumptionGenerator
from tests.www.base_test_case import BaseTestCase


class TestPresenter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_consumptions = self.injector.get(QueryCompanyConsumptionsInteractor)
        self.consumption_generator = self.injector.get(ConsumptionGenerator)
        self.presenter = self.injector.get(CompanyConsumptionsPresenter)

    def test_show_consumptions_from_company(self) -> None:
        now = self.datetime_service.now()
        response: Iterator[ConsumptionQueryResponse] = iter(
            [
                ConsumptionQueryResponse(
                    consumption_date=now,
                    plan_id=uuid4(),
                    product_name="Produkt A",
                    product_description="Beschreibung für Produkt A.",
                    consumption_type=ConsumptionType.raw_materials,
                    paid_price_per_unit=Decimal("7.89"),
                    amount=321,
                ),
                ConsumptionQueryResponse(
                    consumption_date=now,
                    plan_id=uuid4(),
                    product_name="Produkt A",
                    product_description="Beschreibung für Produkt A.",
                    consumption_type=ConsumptionType.means_of_prod,
                    paid_price_per_unit=Decimal("100000"),
                    amount=1,
                ),
            ]
        )
        presentation = self.presenter.present(response)  # DUT

        assert isinstance(presentation, ViewModel)

        assert presentation.consumptions[
            0
        ].consumption_date == self.datetime_formatter.format_datetime(now)
        assert presentation.consumptions[0].product_name == "Produkt A"
        assert (
            presentation.consumptions[0].product_description
            == "Beschreibung für Produkt A."
        )
        assert presentation.consumptions[0].consumption_type == self.translator.gettext(
            "Liquid means of production"
        )
        assert presentation.consumptions[0].price_per_unit == "7.89"
        assert presentation.consumptions[0].amount == "321"
        assert presentation.consumptions[0].price_total == "2532.69"

        assert presentation.consumptions[
            1
        ].consumption_date == self.datetime_formatter.format_datetime(now)
        assert presentation.consumptions[1].product_name == "Produkt A"
        assert (
            presentation.consumptions[1].product_description
            == "Beschreibung für Produkt A."
        )
        assert presentation.consumptions[1].consumption_type == self.translator.gettext(
            "Fixed means of production"
        )
        assert presentation.consumptions[1].price_per_unit == "100000.00"
        assert presentation.consumptions[1].amount == "1"
        assert presentation.consumptions[1].price_total == "100000.00"

    def test_show_consumptions_if_there_is_one_consumption(self) -> None:
        consuming_company = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consuming_company
        )
        interactor_response = self.query_consumptions.execute(company=consuming_company)
        view_model = self.presenter.present(interactor_response)
        assert view_model.show_consumptions

    def test_do_not_show_consumptions_if_there_is_no_consumption_of_querying_company(
        self,
    ) -> None:
        interactor_response: Iterator[ConsumptionQueryResponse] = iter([])
        view_model = self.presenter.present(interactor_response)
        assert not view_model.show_consumptions
