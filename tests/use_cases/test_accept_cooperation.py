from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.accept_cooperation import (
    AcceptCooperation,
    AcceptCooperationRequest,
)
from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase

from .base_test_case import BaseTestCase


class AcceptCooperationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.accept_cooperation = self.injector.get(AcceptCooperation)
        self.get_plan_details_use_case = self.injector.get(GetPlanDetailsUseCase)

    def test_error_is_raised_when_plan_does_not_exist(self) -> None:
        requester = self.company_generator.create_company_record()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=uuid4(), cooperation_id=cooperation
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_not_found

    def test_error_is_raised_when_cooperation_does_not_exist(self) -> None:
        requester = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan, cooperation_id=uuid4()
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.cooperation_not_found
        )

    def test_error_is_raised_when_plan_is_already_in_cooperation(self) -> None:
        requester = self.company_generator.create_company_record()
        cooperation1 = self.cooperation_generator.create_cooperation()
        cooperation2 = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(cooperation=cooperation1)
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan, cooperation_id=cooperation2
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.plan_has_cooperation
        )

    def test_error_is_raised_when_plan_is_public_plan(self) -> None:
        requester = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan(is_public_service=True)
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan, cooperation_id=cooperation
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.plan_is_public_service
        )

    def test_error_is_raised_when_cooperation_was_not_requested(self) -> None:
        requester = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan, cooperation_id=cooperation
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.cooperation_was_not_requested
        )

    def test_error_is_raised_when_requester_is_not_coordinator_of_cooperation(
        self,
    ) -> None:
        requester = self.company_generator.create_company_record()
        coordinator = self.company_generator.create_company_record()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        plan = self.plan_generator.create_plan(requested_cooperation=cooperation)
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan, cooperation_id=cooperation
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.requester_is_not_coordinator
        )

    def test_possible_to_add_plan_to_cooperation(self) -> None:
        requester = self.company_generator.create_company_record()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_cooperation=cooperation)
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan, cooperation_id=cooperation
        )
        response = self.accept_cooperation(request)
        assert not response.is_rejected

    def test_cooperation_is_added_to_plan(self) -> None:
        requester = self.company_generator.create_company_record()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_cooperation=cooperation)
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan, cooperation_id=cooperation
        )
        response = self.accept_cooperation(request)
        assert not response.is_rejected
        self.assert_plan_in_cooperation(plan, cooperation)

    def test_two_cooperating_plans_have_same_prices(self) -> None:
        requester = self.company_generator.create_company_record()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(20), Decimal(30)),
            requested_cooperation=cooperation,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3)),
            requested_cooperation=cooperation,
        )
        request1 = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan1, cooperation_id=cooperation
        )
        request2 = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan2, cooperation_id=cooperation
        )
        self.accept_cooperation(request1)
        self.accept_cooperation(request2)
        assert self.price_checker.get_unit_price(
            plan1
        ) == self.price_checker.get_unit_price(plan2)

    def test_price_of_cooperating_plans_is_correctly_calculated(self) -> None:
        requester = self.company_generator.create_company_record()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)),
            amount=10,
            requested_cooperation=cooperation,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(5), Decimal(3), Decimal(2)),
            amount=10,
            requested_cooperation=cooperation,
        )
        request1 = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan1, cooperation_id=cooperation
        )
        request2 = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan2, cooperation_id=cooperation
        )
        self.accept_cooperation(request1)
        self.accept_cooperation(request2)
        # In total costs of 30h and 20 units -> price should be 1.5h per unit
        assert (
            self.price_checker.get_unit_price(plan1)
            == self.price_checker.get_unit_price(plan2)
            == Decimal("1.5")
        )

    def test_that_cooperation_cannot_be_accepted_twice(self) -> None:
        requester = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(requested_cooperation=cooperation)
        request = AcceptCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        self.accept_cooperation(request)
        response = self.accept_cooperation(request)
        assert response.is_rejected

    def test_that_cooperation_cannot_be_accepted_for_expired_plans(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        requester = self.company_generator.create_company()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(
            requested_cooperation=cooperation, timeframe=1
        )
        request = AcceptCooperationRequest(
            requester_id=requester, plan_id=plan, cooperation_id=cooperation
        )
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.accept_cooperation(request)
        assert response.is_rejected

    def assert_plan_in_cooperation(self, plan: UUID, cooperation: UUID) -> None:
        request = GetPlanDetailsUseCase.Request(plan)
        summary_response = self.get_plan_details_use_case.get_plan_details(request)
        assert summary_response
        assert summary_response.plan_details
        assert summary_response.plan_details.cooperation == cooperation
