from datetime import datetime
from decimal import Decimal

from arbeitszeit.use_cases.query_purchases import QueryPurchases
from arbeitszeit_flask.datetime import RealtimeDatetimeService
from arbeitszeit_web.presenters.show_my_purchases_presenter import (
    ShowMyPurchasesPresenter,
    ViewModel,
)
from tests.data_generators import CompanyGenerator, MemberGenerator, PurchaseGenerator
from tests.use_cases.dependency_injection import get_dependency_injector, injection_test


@injection_test
def test_show_purchases_from_member(
    query_purchases: QueryPurchases,
    member_generator: MemberGenerator,
    purchase_generator: PurchaseGenerator,
):
    injector = get_dependency_injector()
    presenter = injector.get(ShowMyPurchasesPresenter)  # DUT

    now = datetime.now()

    member = member_generator.create_member()
    purchase_generator.create_purchase_by_member(
        buyer=member,
        purchase_date=now,
        amount=123,
        price_per_unit=Decimal(7),
    )
    purchase_generator.create_purchase_by_member(
        buyer=member,
        purchase_date=now,
        amount=2,
        price_per_unit=Decimal(70),
    )

    presentation = presenter.present(query_purchases(member))  # DUT

    assert isinstance(presentation, ViewModel)

    assert presentation.purchases[
        0
    ].purchase_date == RealtimeDatetimeService().format_datetime(now)
    assert presentation.purchases[0].product_name == "Produkt A"
    assert (
        presentation.purchases[0].product_description == "Beschreibung für Produkt A."
    )
    assert presentation.purchases[0].purpose == "Konsum"
    assert presentation.purchases[0].price_per_unit == "7.00"
    assert presentation.purchases[0].amount == "123"
    assert presentation.purchases[0].price_total == "861.00"

    assert presentation.purchases[
        1
    ].purchase_date == RealtimeDatetimeService().format_datetime(now)
    assert presentation.purchases[1].product_name == "Produkt A"
    assert (
        presentation.purchases[1].product_description == "Beschreibung für Produkt A."
    )
    assert presentation.purchases[1].purpose == "Konsum"
    assert presentation.purchases[1].price_per_unit == "70.00"
    assert presentation.purchases[1].amount == "2"
    assert presentation.purchases[1].price_total == "140.00"


@injection_test
def test_show_purchases_from_company(
    query_purchases: QueryPurchases,
    purchase_generator: PurchaseGenerator,
    company_generator: CompanyGenerator,
):
    injector = get_dependency_injector()
    presenter = injector.get(ShowMyPurchasesPresenter)  # DUT

    now = datetime.now()

    company = company_generator.create_company()
    purchase_generator.create_purchase_by_company(
        buyer=company,
        purchase_date=now,
        amount=321,
        price_per_unit=Decimal(7.89),
    )

    purchase_generator.create_purchase_by_company(
        buyer=company,
        purchase_date=now,
        amount=1,
        price_per_unit=Decimal(100000),
    )

    presentation = presenter.present(query_purchases(company))  # DUT

    assert isinstance(presentation, ViewModel)

    assert presentation.purchases[
        0
    ].purchase_date == RealtimeDatetimeService().format_datetime(now)
    assert presentation.purchases[0].product_name == "Produkt A"
    assert (
        presentation.purchases[0].product_description == "Beschreibung für Produkt A."
    )
    assert presentation.purchases[0].purpose == "Prod.mittel"
    assert presentation.purchases[0].price_per_unit == "7.89"
    assert presentation.purchases[0].amount == "321"
    assert presentation.purchases[0].price_total == "2532.69"

    assert presentation.purchases[
        1
    ].purchase_date == RealtimeDatetimeService().format_datetime(now)
    assert presentation.purchases[1].product_name == "Produkt A"
    assert (
        presentation.purchases[1].product_description == "Beschreibung für Produkt A."
    )
    assert presentation.purchases[1].purpose == "Prod.mittel"
    assert presentation.purchases[1].price_per_unit == "100000"
    assert presentation.purchases[1].amount == "1"
    assert presentation.purchases[1].price_total == "100000"
