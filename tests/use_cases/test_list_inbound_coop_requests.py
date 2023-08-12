from datetime import datetime, timedelta
from uuid import uuid4

from arbeitszeit.records import Plan
from arbeitszeit.use_cases.list_inbound_coop_requests import (
    ListInboundCoopRequests,
    ListInboundCoopRequestsRequest,
    ListInboundCoopRequestsResponse,
)
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ListInboundCoopRequests)

    def test_emtpy_list_is_returned_when_cooperation_is_not_found(self):
        response = self.use_case(ListInboundCoopRequestsRequest(uuid4()))
        assert len(response.cooperation_requests) == 0

    def test_empty_list_is_returned_when_there_are_no_requests_for_coordinator(
        self,
    ):
        coordinator = self.company_generator.create_company_record()
        coop = self.coop_generator.create_cooperation()
        self.plan_generator.create_plan(requested_cooperation=coop)
        response = self.use_case(ListInboundCoopRequestsRequest(coordinator.id))
        assert len(response.cooperation_requests) == 0

    def test_correct_plans_are_returned_when_plans_request_cooperation(
        self,
    ):
        coordinator = self.company_generator.create_company()
        coop = self.coop_generator.create_cooperation(coordinator=coordinator)
        requesting_plan1 = self.plan_generator.create_plan(requested_cooperation=coop)
        requesting_plan2 = self.plan_generator.create_plan(requested_cooperation=coop)
        response = self.use_case(ListInboundCoopRequestsRequest(coordinator))
        assert len(response.cooperation_requests) == 2
        assert self.plan_in_list(requesting_plan1, response)
        assert self.plan_in_list(requesting_plan2, response)

    def test_that_requests_for_expired_plans_are_not_shown(
        self,
    ):
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        coordinator = self.company_generator.create_company_record()
        coop = self.coop_generator.create_cooperation(coordinator=coordinator)
        self.plan_generator.create_plan(requested_cooperation=coop, timeframe=1)
        self.plan_generator.create_plan(requested_cooperation=coop, timeframe=5)
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.use_case(ListInboundCoopRequestsRequest(coordinator.id))
        assert len(response.cooperation_requests) == 1

    def plan_in_list(
        self, plan: Plan, response: ListInboundCoopRequestsResponse
    ) -> bool:
        for listed_request in response.cooperation_requests:
            if plan.id == listed_request.plan_id:
                return True
        return False
