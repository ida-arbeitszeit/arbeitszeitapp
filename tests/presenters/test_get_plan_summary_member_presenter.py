from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit.use_cases.get_plan_summary_member import PlanSummarySuccess
from arbeitszeit_web.get_plan_summary_member import GetPlanSummarySuccessPresenter
from tests.plan_summary import FakePlanSummaryService
from tests.translator import FakeTranslator

TESTING_RESPONSE_MODEL = PlanSummarySuccess(
    plan_summary=BusinessPlanSummary(
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
        price_per_unit=Decimal("0.061"),
        is_available=True,
        is_cooperating=True,
        cooperation=uuid4(),
    )
)


class GetPlanSummarySuccessPresenterTests(TestCase):
    def setUp(self) -> None:
        self.translator = FakeTranslator()
        self.plan_summary_service = FakePlanSummaryService()
        self.presenter = GetPlanSummarySuccessPresenter(
            self.translator, self.plan_summary_service
        )
