from datetime import datetime

from arbeitszeit_flask.database.repositories import PurchaseRepository
from tests.data_generators import CompanyGenerator, MemberGenerator, PurchaseGenerator

from .dependency_injection import injection_test


@injection_test
def test_repository_for_member(
    repository: PurchaseRepository,
    purchase_generator: PurchaseGenerator,
    member_generator: MemberGenerator,
) -> None:
    user = member_generator.create_member()
    earlier_purchase = purchase_generator.create_purchase_by_member(
        buyer=user, purchase_date=datetime(2000, 1, 1)
    )
    later_purchase = purchase_generator.create_purchase_by_member(
        buyer=user, purchase_date=datetime(2001, 2, 2)
    )
    result = list(repository.get_purchases_descending_by_date(user))
    assert [later_purchase, earlier_purchase] == result


@injection_test
def test_repository_for_company(
    repository: PurchaseRepository,
    purchase_generator: PurchaseGenerator,
    company_generator: CompanyGenerator,
) -> None:
    user = company_generator.create_company()
    earlier_purchase = purchase_generator.create_purchase_by_company(
        buyer=user, purchase_date=datetime(2000, 1, 1)
    )
    later_purchase = purchase_generator.create_purchase_by_company(
        buyer=user, purchase_date=datetime(2001, 2, 2)
    )
    result = list(repository.get_purchases_descending_by_date(user))
    assert [later_purchase, earlier_purchase] == result
