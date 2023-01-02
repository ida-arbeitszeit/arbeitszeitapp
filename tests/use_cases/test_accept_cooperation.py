from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import AcceptCooperation, AcceptCooperationRequest
from tests.data_generators import CooperationGenerator

from .base_test_case import BaseTestCase


class AcceptCooperationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.accept_cooperation = self.injector.get(AcceptCooperation)

    def test_error_is_raised_when_plan_does_not_exist(self) -> None:
        requester = self.company_generator.create_company_entity()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=uuid4(), cooperation_id=cooperation.id
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_not_found

    def test_error_is_raised_when_cooperation_does_not_exist(self) -> None:
        requester = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan()
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan.id, cooperation_id=uuid4()
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.cooperation_not_found
        )

    def test_error_is_raised_when_plan_is_already_in_cooperation(self) -> None:
        requester = self.company_generator.create_company_entity()
        cooperation1 = self.cooperation_generator.create_cooperation()
        cooperation2 = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(
            activation_date=datetime.now(), cooperation=cooperation1
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation2.id
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.plan_has_cooperation
        )

    def test_error_is_raised_when_plan_is_public_plan(self) -> None:
        requester = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            activation_date=datetime.now(), is_public_service=True
        )
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason == response.RejectionReason.plan_is_public_service
        )

    def test_error_is_raised_when_cooperation_was_not_requested(self) -> None:
        requester = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(activation_date=datetime.now())
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
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
        requester = self.company_generator.create_company_entity()
        coordinator = self.company_generator.create_company_entity()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=coordinator
        )
        plan = self.plan_generator.create_plan(
            activation_date=datetime.now(), requested_cooperation=cooperation
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
        )
        response = self.accept_cooperation(request)
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.requester_is_not_coordinator
        )

    def test_possible_to_add_plan_to_cooperation(self) -> None:
        requester = self.company_generator.create_company_entity()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(
            activation_date=datetime.now(), requested_cooperation=cooperation
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
        )
        response = self.accept_cooperation(request)
        assert not response.is_rejected

    def test_cooperation_is_added_to_plan(self) -> None:
        requester = self.company_generator.create_company_entity()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(
            activation_date=datetime.now(), requested_cooperation=cooperation
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
        )
        self.accept_cooperation(request)
        assert plan.cooperation == cooperation.id

    def test_two_cooperating_plans_have_same_prices(self) -> None:
        requester = self.company_generator.create_company_entity()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan1 = self.plan_generator.create_plan(
            activation_date=datetime.now(),
            costs=ProductionCosts(Decimal(10), Decimal(20), Decimal(30)),
            requested_cooperation=cooperation,
        )
        plan2 = self.plan_generator.create_plan(
            activation_date=datetime.now(),
            costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3)),
            requested_cooperation=cooperation,
        )
        request1 = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan1.id, cooperation_id=cooperation.id
        )
        request2 = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan2.id, cooperation_id=cooperation.id
        )
        self.accept_cooperation(request1)
        self.accept_cooperation(request2)
        assert self.price_checker.get_unit_price(
            plan1.id
        ) == self.price_checker.get_unit_price(plan2.id)

    def test_price_of_cooperating_plans_is_correctly_calculated(self) -> None:
        requester = self.company_generator.create_company_entity()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan1 = self.plan_generator.create_plan(
            activation_date=datetime.now(),
            costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)),
            amount=10,
            requested_cooperation=cooperation,
        )
        plan2 = self.plan_generator.create_plan(
            activation_date=datetime.now(),
            costs=ProductionCosts(Decimal(5), Decimal(3), Decimal(2)),
            amount=10,
            requested_cooperation=cooperation,
        )
        request1 = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan1.id, cooperation_id=cooperation.id
        )
        request2 = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan2.id, cooperation_id=cooperation.id
        )
        self.accept_cooperation(request1)
        self.accept_cooperation(request2)
        # In total costs of 30h and 20 units -> price should be 1.5h per unit
        assert (
            self.price_checker.get_unit_price(plan1.id)
            == self.price_checker.get_unit_price(plan2.id)
            == Decimal("1.5")
        )

    def test_that_attribute_requested_cooperation_is_set_to_none_after_start_of_cooperation(
        self,
    ) -> None:
        requester = self.company_generator.create_company_entity()
        cooperation = self.cooperation_generator.create_cooperation(
            coordinator=requester
        )
        plan = self.plan_generator.create_plan(
            activation_date=datetime.now(), requested_cooperation=cooperation
        )
        request = AcceptCooperationRequest(
            requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
        )
        assert plan.requested_cooperation == cooperation.id
        self.accept_cooperation(request)
        assert plan.requested_cooperation is None
