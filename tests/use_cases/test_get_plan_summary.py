from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_plan_summary import GetPlanSummaryUseCase
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.use_case = self.injector.get(GetPlanSummaryUseCase)
        self.company = self.company_generator.create_company_entity()

    def test_that_failure_is_returned_when_plan_does_not_exist(self) -> None:
        self.assertIsInstance(
            self.use_case.get_plan_summary(uuid4()), GetPlanSummaryUseCase.Failure
        )

    def test_plan_summary_success_is_returned_when_plan_exists(self):
        plan = self.plan_generator.create_plan()
        self.assertIsInstance(
            self.use_case.get_plan_summary(plan.id), GetPlanSummaryUseCase.Success
        )

    def test_plan_summary_is_returned_when_plan_exists(self):
        plan = self.plan_generator.create_plan()
        plan_summary_success = self.use_case.get_plan_summary(plan.id)
        assert isinstance(plan_summary_success, GetPlanSummaryUseCase.Success)
        self.assertTrue(plan_summary_success.plan_summary)
