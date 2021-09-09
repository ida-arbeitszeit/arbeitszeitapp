from datetime import datetime

from project.database.repositories import ProductOfferRepository
from tests.data_generators import PlanGenerator

from .dependency_injection import injection_test


@injection_test
def tests_offers_can_be_created(
    offer_repository: ProductOfferRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    assert not len(offer_repository)
    offer_repository.create_offer(
        plan=plan,
        creation_datetime=datetime.now(),
        name="testname",
        description="testdescription",
    )
    assert len(offer_repository)
