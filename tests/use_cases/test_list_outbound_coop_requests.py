from datetime import datetime
from uuid import uuid4

from arbeitszeit.entities import Plan
from arbeitszeit.use_cases import (
    ListOutboundCoopRequests,
    ListOutboundCoopRequestsRequest,
    ListOutboundCoopRequestsResponse,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import injection_test


def plan_in_list(plan: Plan, response: ListOutboundCoopRequestsResponse) -> bool:
    for listed_request in response.cooperation_requests:
        if plan.id == listed_request.plan_id:
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
    plan_generator.create_plan(requested_cooperation=coop, activation_date=datetime.min)
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
        requested_cooperation=coop, activation_date=datetime.min, planner=requester
    )
    requesting_plan2 = plan_generator.create_plan(
        requested_cooperation=coop, activation_date=datetime.min, planner=requester
    )
    response = list_requests(ListOutboundCoopRequestsRequest(requester))
    assert len(response.cooperation_requests) == 2
    assert plan_in_list(requesting_plan1, response)
    assert plan_in_list(requesting_plan2, response)
