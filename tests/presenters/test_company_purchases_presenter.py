from decimal import Decimal
from typing import Iterator
from uuid import uuid4

from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases.query_company_purchases import (
    PurchaseQueryResponse,
    QueryCompanyPurchases,
)
from arbeitszeit_web.www.presenters.company_purchases_presenter import (
    CompanyPurchasesPresenter,
    ViewModel,
)
from tests.data_generators import CompanyGenerator, PurchaseGenerator
from tests.datetime_service import FakeDatetimeService
from tests.presenters.base_test_case import BaseTestCase
from tests.translator import FakeTranslator


class TestPresenter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.query_purchases = self.injector.get(QueryCompanyPurchases)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(CompanyPurchasesPresenter)

    def test_show_purchases_from_company(self) -> None:
        now = self.datetime_service.now()
        response: Iterator[PurchaseQueryResponse] = iter(
            [
                PurchaseQueryResponse(
                    purchase_date=now,
                    plan_id=uuid4(),
                    product_name="Produkt A",
                    product_description="Beschreibung für Produkt A.",
                    purpose=PurposesOfPurchases.raw_materials,
                    price_per_unit=Decimal("7.89"),
                    amount=321,
                ),
                PurchaseQueryResponse(
                    purchase_date=now,
                    plan_id=uuid4(),
                    product_name="Produkt A",
                    product_description="Beschreibung für Produkt A.",
                    purpose=PurposesOfPurchases.means_of_prod,
                    price_per_unit=Decimal("100000"),
                    amount=1,
                ),
            ]
        )
        presentation = self.presenter.present(response)  # DUT

        assert isinstance(presentation, ViewModel)

        assert presentation.purchases[
            0
        ].purchase_date == FakeDatetimeService().format_datetime(
            now, zone="Europe/Berlin"
        )
        assert presentation.purchases[0].product_name == "Produkt A"
        assert (
            presentation.purchases[0].product_description
            == "Beschreibung für Produkt A."
        )
        assert presentation.purchases[0].purpose == self.translator.gettext(
            "Liquid means of production"
        )
        assert presentation.purchases[0].price_per_unit == "7.89"
        assert presentation.purchases[0].amount == "321"
        assert presentation.purchases[0].price_total == "2532.69"

        assert presentation.purchases[
            1
        ].purchase_date == FakeDatetimeService().format_datetime(
            now, zone="Europe/Berlin"
        )
        assert presentation.purchases[1].product_name == "Produkt A"
        assert (
            presentation.purchases[1].product_description
            == "Beschreibung für Produkt A."
        )
        assert presentation.purchases[1].purpose == self.translator.gettext(
            "Fixed means of production"
        )
        assert presentation.purchases[1].price_per_unit == "100000.00"
        assert presentation.purchases[1].amount == "1"
        assert presentation.purchases[1].price_total == "100000.00"

    def test_show_purchases_if_there_is_one_purchase(self) -> None:
        buying_company = self.company_generator.create_company()
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buying_company
        )
        use_case_response = self.query_purchases(company=buying_company)
        view_model = self.presenter.present(use_case_response)
        assert view_model.show_purchases

    def test_do_not_show_purchases_if_there_is_no_purchase_of_querying_company(
        self,
    ) -> None:
        use_case_response: Iterator[PurchaseQueryResponse] = iter([])
        view_model = self.presenter.present(use_case_response)
        assert not view_model.show_purchases
