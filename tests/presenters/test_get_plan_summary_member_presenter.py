from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases.get_plan_summary_member import GetPlanSummaryMember
from arbeitszeit_web.get_plan_summary_member import GetPlanSummarySuccessPresenter
from tests.presenters.dependency_injection import injection_test
from tests.presenters.url_index import PayConsumerProductUrlIndexImpl


class PresenterTests(TestCase):
    """
    some functionality tested in tests/presenters/test_plan_summary_service.py
    """

    @injection_test
    def setUp(
        self,
        url_index: PayConsumerProductUrlIndexImpl,
        presenter: GetPlanSummarySuccessPresenter,
    ) -> None:
        self.url_index = url_index
        self.presenter = presenter

    def test_that_pay_product_url_is_shown_correctly(self):
        use_case_response = self.get_use_case_response()
        view_model = self.presenter.present(use_case_response)
        self.assertEqual(
            view_model.pay_product_url,
            self.url_index.get_pay_consumer_product_url(
                amount=1, plan_id=use_case_response.plan_summary.plan_id
            ),
        )

    def get_use_case_response(self):
        return GetPlanSummaryMember.Success(
            plan_summary=PlanSummary(
                plan_id=uuid4(),
                is_active=True,
                planner_id=uuid4(),
                planner_name="planner name",
                product_name="test product name",
                description="test description",
                active_days=5,
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
                creation_date=datetime.now(),
                approval_date=None,
                expiration_date=None,
            ),
        )
