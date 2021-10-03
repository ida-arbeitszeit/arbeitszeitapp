from datetime import datetime

from project.database.repositories import PurchaseRepository
from tests.data_generators import MemberGenerator, PurchaseGenerator

from .dependency_injection import injection_test


@injection_test
def test_repository(
    repository: PurchaseRepository,
    purchase_generator: PurchaseGenerator,
    member_generator: MemberGenerator,
) -> None:
    user = member_generator.create_member()
    earlier_purchase = purchase_generator.create_purchase(
        buyer=user, purchase_date=datetime(2000, 1, 1)
    )
    later_purchase = purchase_generator.create_purchase(
        buyer=user, purchase_date=datetime(2001, 2, 2)
    )
    result = list(repository.get_purchases_descending_by_date(user))
    assert [later_purchase, earlier_purchase] == result
