from arbeitszeit.use_cases import QueryPurchases
from tests.data_generators import CompanyGenerator, MemberGenerator, PurchaseGenerator
from tests.datetime_service import TestDatetimeService
from tests.dependency_injection import injection_test
from tests.repositories import PurchaseRepository


@injection_test
def test_that_no_purchase_is_returned_when_searching_an_empty_repo(
    query_purchases: QueryPurchases,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member = member_generator.create_member()
    results = list(query_purchases(member))
    assert not results
    company = company_generator.create_company()
    results = list(query_purchases(company))
    assert not results


@injection_test
def test_that_correct_purchases_are_returned(
    query_purchases: QueryPurchases,
    member_generator: MemberGenerator,
    purchase_generator: PurchaseGenerator,
    company_generator: CompanyGenerator,
    repository: PurchaseRepository,
):
    member = member_generator.create_member()
    company = company_generator.create_company()
    expected_purchase_member = purchase_generator.create_purchase(buyer=member)
    expected_purchase_company = purchase_generator.create_purchase(buyer=company)
    repository.add(expected_purchase_member)
    repository.add(expected_purchase_company)
    results = list(query_purchases(member))
    assert len(results) == 1
    assert expected_purchase_member in results
    assert expected_purchase_company not in results
    results = list(query_purchases(company))
    assert len(results) == 1
    assert expected_purchase_company in results
    assert expected_purchase_member not in results


@injection_test
def test_that_purchases_are_returned_in_correct_order_when_member_queries(
    query_purchases: QueryPurchases,
    member_generator: MemberGenerator,
    purchase_generator: PurchaseGenerator,
    repository: PurchaseRepository,
):
    member = member_generator.create_member()
    expected_recent_purchase = purchase_generator.create_purchase(
        buyer=member, purchase_date=TestDatetimeService().now_minus_one_day()
    )
    expected_older_purchase = purchase_generator.create_purchase(
        buyer=member, purchase_date=TestDatetimeService().now_minus_two_days()
    )
    repository.add(expected_older_purchase)  # adding older purchase first
    repository.add(expected_recent_purchase)
    results = list(query_purchases(member))
    assert results[0] == expected_recent_purchase  # more recent purchase is first


@injection_test
def test_that_purchases_are_returned_in_correct_order_when_company_queries(
    query_purchases: QueryPurchases,
    purchase_generator: PurchaseGenerator,
    company_generator: CompanyGenerator,
    repository: PurchaseRepository,
):
    company = company_generator.create_company()
    expected_recent_purchase = purchase_generator.create_purchase(
        buyer=company, purchase_date=TestDatetimeService().now_minus_one_day()
    )
    expected_older_purchase = purchase_generator.create_purchase(
        buyer=company, purchase_date=TestDatetimeService().now_minus_two_days()
    )
    repository.add(expected_older_purchase)  # adding older purchase first
    repository.add(expected_recent_purchase)
    results = list(query_purchases(company))
    assert results[0] == expected_recent_purchase  # more recent purchase is first
