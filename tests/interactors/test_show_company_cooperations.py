from datetime import timedelta
from uuid import uuid4

from arbeitszeit.interactors.show_company_cooperations import (
    Request,
    ShowCompanyCooperationsInteractor,
)
from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase


class InboundCooperationRequestsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ShowCompanyCooperationsInteractor)

    def test_emtpy_list_is_returned_when_cooperation_is_not_found(self) -> None:
        response = self.interactor.show_company_cooperations(Request(uuid4()))
        assert len(response.inbound_cooperation_requests) == 0

    def test_empty_list_is_returned_when_there_are_no_requests_for_coordinator(
        self,
    ) -> None:
        coordinator = self.company_generator.create_company_record()
        coop = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(requested_cooperation=coop)
        response = self.interactor.show_company_cooperations(Request(coordinator.id))
        assert len(response.inbound_cooperation_requests) == 0

    def test_correct_plans_are_returned_when_plans_request_cooperation(
        self,
    ) -> None:
        coordinator = self.company_generator.create_company()
        coop = self.cooperation_generator.create_cooperation(coordinator=coordinator)
        requesting_plan1 = self.plan_generator.create_plan(requested_cooperation=coop)
        requesting_plan2 = self.plan_generator.create_plan(requested_cooperation=coop)
        response = self.interactor.show_company_cooperations(Request(coordinator))
        assert len(response.inbound_cooperation_requests) == 2
        assert requesting_plan1 in [
            request.plan_id for request in response.inbound_cooperation_requests
        ]
        assert requesting_plan2 in [
            request.plan_id for request in response.inbound_cooperation_requests
        ]

    def test_that_requests_for_expired_plans_are_not_shown(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        coordinator = self.company_generator.create_company_record()
        coop = self.cooperation_generator.create_cooperation(coordinator=coordinator)
        self.plan_generator.create_plan(requested_cooperation=coop, timeframe=1)
        self.plan_generator.create_plan(requested_cooperation=coop, timeframe=5)
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.show_company_cooperations(Request(coordinator.id))
        assert len(response.inbound_cooperation_requests) == 1


class OutboundCoopRequestsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ShowCompanyCooperationsInteractor)

    def test_emtpy_list_is_returned_when_cooperation_is_not_found(self) -> None:
        response = self.interactor.show_company_cooperations(Request(uuid4()))
        self.assertEqual(len(response.outbound_cooperation_requests), 0)

    def test_empty_list_is_returned_when_there_are_no_outbound_requests(self) -> None:
        requester = self.company_generator.create_company()
        coop = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(requested_cooperation=coop)
        response = self.interactor.show_company_cooperations(Request(requester))
        self.assertEqual(len(response.outbound_cooperation_requests), 0)

    def test_correct_plans_are_returned_when_there_are_outbound_requests(self) -> None:
        requester = self.company_generator.create_company()
        coop = self.cooperation_generator.create_cooperation()
        requesting_plan1 = self.plan_generator.create_plan(
            requested_cooperation=coop, planner=requester
        )
        requesting_plan2 = self.plan_generator.create_plan(
            requested_cooperation=coop, planner=requester
        )
        response = self.interactor.show_company_cooperations(Request(requester))
        self.assertEqual(len(response.outbound_cooperation_requests), 2)
        assert requesting_plan1 in [
            request.plan_id for request in response.outbound_cooperation_requests
        ]
        assert requesting_plan2 in [
            request.plan_id for request in response.outbound_cooperation_requests
        ]

    def test_that_requests_for_expired_plans_are_not_shown(self) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        requester = self.company_generator.create_company()
        coop = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(
            requested_cooperation=coop, planner=requester, timeframe=1
        )
        self.plan_generator.create_plan(
            requested_cooperation=coop, planner=requester, timeframe=5
        )
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.show_company_cooperations(Request(requester))
        self.assertEqual(len(response.outbound_cooperation_requests), 1)
