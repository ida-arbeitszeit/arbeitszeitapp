from uuid import uuid4

from arbeitszeit.interactors.list_my_cooperating_plans import (
    ListMyCooperatingPlansInteractor,
)

from .base_test_case import BaseTestCase


class InteractorTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ListMyCooperatingPlansInteractor)

    def test_failure_is_raised_if_requesting_company_does_not_exist(self) -> None:
        with self.assertRaises(ListMyCooperatingPlansInteractor.Failure):
            request = ListMyCooperatingPlansInteractor.Request(company=uuid4())
            self.interactor.list_cooperations(request)

    def test_response_is_returned_if_requester_does_exist(self) -> None:
        requester = self.company_generator.create_company()
        request = ListMyCooperatingPlansInteractor.Request(company=requester)
        result = self.interactor.list_cooperations(request=request)
        assert isinstance(result, ListMyCooperatingPlansInteractor.Response)

    def test_no_plans_are_returned_if_requester_has_no_plans(self) -> None:
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansInteractor.Request(company=company)
        result = self.interactor.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 0

    def test_no_plans_are_returned_if_requester_has_no_active_plans(self) -> None:
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansInteractor.Request(company=company)
        self.plan_generator.create_plan(planner=company, approved=False)
        result = self.interactor.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 0

    def test_no_plans_are_returned_if_requester_has_no_cooperating_plans(self) -> None:
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansInteractor.Request(company=company)
        self.plan_generator.create_plan(planner=company, cooperation=None)
        result = self.interactor.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 0

    def test_one_plan_is_returned_if_requester_has_one_active_cooperating_plan(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansInteractor.Request(company=company)
        self.plan_generator.create_plan(planner=company, cooperation=coop)
        result = self.interactor.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 1

    def test_returned_plan_has_correct_attributes(self) -> None:
        expected_coop_name = "Test Cooperation"
        expected_product_name = "test product name"
        coop = self.cooperation_generator.create_cooperation(name=expected_coop_name)
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansInteractor.Request(company=company)
        plan = self.plan_generator.create_plan(
            planner=company, cooperation=coop, product_name=expected_product_name
        )
        result = self.interactor.list_cooperations(request=request)
        cooperating_plan = result.cooperating_plans[0]
        assert cooperating_plan.coop_id == coop
        assert cooperating_plan.coop_name == expected_coop_name
        assert cooperating_plan.plan_id == plan
        assert cooperating_plan.plan_name == expected_product_name

    def test_two_plans_are_returned_if_requester_has_two_active_cooperating_plan(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        company = self.company_generator.create_company()
        request = ListMyCooperatingPlansInteractor.Request(company=company)
        self.plan_generator.create_plan(planner=company, cooperation=coop)
        self.plan_generator.create_plan(planner=company, cooperation=coop)
        result = self.interactor.list_cooperations(request=request)
        assert len(result.cooperating_plans) == 2
