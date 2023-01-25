from uuid import uuid4

from arbeitszeit.use_cases.list_my_cooperating_plans import (
    ListMyCooperatingPlansUseCase,
)

from .base_test_case import BaseTestCase


class UseCaseTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ListMyCooperatingPlansUseCase)

    def test_failure_is_raised_if_requesting_company_does_not_exist(self) -> None:
        with self.assertRaises(ListMyCooperatingPlansUseCase.Failure):
            request = ListMyCooperatingPlansUseCase.Request(company=uuid4())
            self.use_case.list_cooperations(request)

    def test_response_is_returned_if_requester_does_exist(self) -> None:
        requester = self.company_generator.create_company()
        request = ListMyCooperatingPlansUseCase.Request(company=requester)
        result = self.use_case.list_cooperations(request=request)
        assert isinstance(result, ListMyCooperatingPlansUseCase.Response)

    def test_no_plans_are_returned_if_requester_has_no_plans(self) -> None:
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansUseCase.Request(company=company)
        result = self.use_case.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 0

    def test_no_plans_are_returned_if_requester_has_no_active_plans(self) -> None:
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansUseCase.Request(company=company)
        self.plan_generator.create_plan(planner=company, approved=False)
        result = self.use_case.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 0

    def test_no_plans_are_returned_if_requester_has_no_cooperating_plans(self) -> None:
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansUseCase.Request(company=company)
        self.plan_generator.create_plan(planner=company, cooperation=None)
        result = self.use_case.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 0

    def test_one_plan_is_returned_if_requester_has_one_active_cooperating_plan(
        self,
    ) -> None:
        coop = self.coop_generator.create_cooperation()
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansUseCase.Request(company=company)
        self.plan_generator.create_plan(planner=company, cooperation=coop)
        result = self.use_case.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 1

    def test_returned_plan_has_correct_attributes(self) -> None:
        coop = self.coop_generator.create_cooperation()
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansUseCase.Request(company=company)
        plan = self.plan_generator.create_plan(planner=company, cooperation=coop)
        result = self.use_case.list_cooperations(request=request)
        cooperating_plan = result.cooperating_plans[0]
        assert cooperating_plan.coop_id == coop.id
        assert cooperating_plan.coop_name == coop.name
        assert cooperating_plan.plan_id == plan.id
        assert cooperating_plan.plan_name == plan.prd_name

    def test_two_plans_are_returned_if_requester_has_two_active_cooperating_plan(
        self,
    ) -> None:
        coop = self.coop_generator.create_cooperation()
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansUseCase.Request(company=company)
        self.plan_generator.create_plan(planner=company, cooperation=coop)
        self.plan_generator.create_plan(planner=company, cooperation=coop)
        result = self.use_case.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 2
