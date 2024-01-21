from datetime import datetime, timedelta
from uuid import UUID, uuid4

from arbeitszeit.use_cases.list_outbound_coop_requests import (
    ListOutboundCoopRequests,
    ListOutboundCoopRequestsRequest,
    ListOutboundCoopRequestsResponse,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test


def plan_in_list(plan: UUID, response: ListOutboundCoopRequestsResponse) -> bool:
    for listed_request in response.cooperation_requests:
        if plan == listed_request.plan_id:
            return True
    return False


@injection_test
def test_emtpy_list_is_returned_when_cooperation_is_not_found(
    list_requests: ListOutboundCoopRequests,
):
    response = list_requests(ListOutboundCoopRequestsRequest(uuid4()))
    assert len(response.cooperation_requests) == 0


@injection_test
def test_empty_list_is_returned_when_there_are_no_outbound_requests(
    list_requests: ListOutboundCoopRequests,
    coop_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    coop = coop_generator.create_cooperation()
    plan_generator.create_plan(requested_cooperation=coop)
    response = list_requests(ListOutboundCoopRequestsRequest(requester))
    assert len(response.cooperation_requests) == 0


@injection_test
def test_correct_plans_are_returned_when_there_are_outbound_requests(
    list_requests: ListOutboundCoopRequests,
    coop_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    coop = coop_generator.create_cooperation()
    requesting_plan1 = plan_generator.create_plan(
        requested_cooperation=coop, planner=requester
    )
    requesting_plan2 = plan_generator.create_plan(
        requested_cooperation=coop, planner=requester
    )
    response = list_requests(ListOutboundCoopRequestsRequest(requester))
    assert len(response.cooperation_requests) == 2
    assert plan_in_list(requesting_plan1, response)
    assert plan_in_list(requesting_plan2, response)


@injection_test
def test_that_requests_for_expired_plans_are_not_shown(
    list_requests: ListOutboundCoopRequests,
    coop_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
    datetime_service: FakeDatetimeService,
):
    datetime_service.freeze_time(datetime(2000, 1, 1))
    requester = company_generator.create_company()
    coop = coop_generator.create_cooperation()
    plan_generator.create_plan(
        requested_cooperation=coop, planner=requester, timeframe=1
    )
    plan_generator.create_plan(
        requested_cooperation=coop, planner=requester, timeframe=5
    )
    datetime_service.advance_time(timedelta(days=2))
    response = list_requests(ListOutboundCoopRequestsRequest(requester))
    assert len(response.cooperation_requests) == 1
