from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_plan_summary import PlanSummaryResponse
from arbeitszeit_web.get_plan_summary import GetPlanSummaryPresenter

TESTING_RESPONSE_MODEL = PlanSummaryResponse(
    plan_id=uuid4(),
    is_active=True,
    planner_id=uuid4(),
    product_name="test product name",
    description="test description",
    timeframe=7,
    production_unit="Piece",
    amount=100,
    means_cost=Decimal(1),
    resources_cost=Decimal(2),
    labour_cost=Decimal(3),
    is_public_service=False,
    price_per_unit=Decimal(0.06),
)


class GetPlanSummaryPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = GetPlanSummaryPresenter()

    def test_plan_id_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.plan_id, ("Plan-ID", str(TESTING_RESPONSE_MODEL.plan_id))
        )
