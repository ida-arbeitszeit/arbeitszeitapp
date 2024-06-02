from datetime import datetime, timedelta
from uuid import UUID, uuid4

from arbeitszeit.use_cases.list_outbound_coop_requests import (
    ListOutboundCoopRequests,
    ListOutboundCoopRequestsRequest,
    ListOutboundCoopRequestsResponse,
)
from tests.use_cases.base_test_case import BaseTestCase


class ListOutboundCoopRequestsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.list_requests = self.injector.get(ListOutboundCoopRequests)

    def test_emtpy_list_is_returned_when_cooperation_is_not_found(self) -> None:
        response = self.list_requests(ListOutboundCoopRequestsRequest(uuid4()))
        self.assertEqual(len(response.cooperation_requests), 0)

    def test_empty_list_is_returned_when_there_are_no_outbound_requests(self) -> None:
        requester = self.company_generator.create_company()
        coop = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(requested_cooperation=coop)
        response = self.list_requests(ListOutboundCoopRequestsRequest(requester))
        self.assertEqual(len(response.cooperation_requests), 0)

    def test_correct_plans_are_returned_when_there_are_outbound_requests(self) -> None:
        requester = self.company_generator.create_company()
        coop = self.cooperation_generator.create_cooperation()
        requesting_plan1 = self.plan_generator.create_plan(
            requested_cooperation=coop, planner=requester
        )
        requesting_plan2 = self.plan_generator.create_plan(
            requested_cooperation=coop, planner=requester
        )
        response = self.list_requests(ListOutboundCoopRequestsRequest(requester))
        self.assertEqual(len(response.cooperation_requests), 2)
        self.assertTrue(plan_in_list(requesting_plan1, response))
        self.assertTrue(plan_in_list(requesting_plan2, response))

    def test_that_requests_for_expired_plans_are_not_shown(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        requester = self.company_generator.create_company()
        coop = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(
            requested_cooperation=coop, planner=requester, timeframe=1
        )
        self.plan_generator.create_plan(
            requested_cooperation=coop, planner=requester, timeframe=5
        )
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.list_requests(ListOutboundCoopRequestsRequest(requester))
        self.assertEqual(len(response.cooperation_requests), 1)


def plan_in_list(plan: UUID, response: ListOutboundCoopRequestsResponse) -> bool:
    for listed_request in response.cooperation_requests:
        if plan == listed_request.plan_id:
            return True
    return False
