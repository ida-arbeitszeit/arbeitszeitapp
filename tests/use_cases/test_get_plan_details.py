from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.use_case = self.injector.get(GetPlanDetailsUseCase)
        self.company = self.company_generator.create_company_entity()

    def test_that_none_is_returned_when_plan_does_not_exist(self) -> None:
        request = GetPlanDetailsUseCase.Request(uuid4())
        self.assertFalse(self.use_case.get_plan_details(request))

    def test_plan_details_is_returned_when_plan_exists(self):
        plan = self.plan_generator.create_plan()
        request = GetPlanDetailsUseCase.Request(plan.id)
        self.assertTrue(self.use_case.get_plan_details(request))
