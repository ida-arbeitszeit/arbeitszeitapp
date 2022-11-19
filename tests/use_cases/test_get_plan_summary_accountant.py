from uuid import uuid4

from arbeitszeit.use_cases.get_plan_summary_accountant import GetPlanSummaryAccountant
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(GetPlanSummaryAccountant)
        self.company = self.company_generator.create_company_entity()

    def test_that_failure_is_returned_when_plan_does_not_exist(self) -> None:
        self.assertIsInstance(self.use_case(uuid4()), GetPlanSummaryAccountant.Failure)

    def test_plan_summary_success_is_returned_when_plan_exists(self):
        plan = self.plan_generator.create_plan()
        self.assertIsInstance(self.use_case(plan.id), GetPlanSummaryAccountant.Success)

    def test_plan_summary_is_returned_when_plan_exists(self):
        plan = self.plan_generator.create_plan()
        plan_summary_success = self.use_case(plan.id)
        assert isinstance(plan_summary_success, GetPlanSummaryAccountant.Success)
        self.assertTrue(plan_summary_success.plan_summary)
