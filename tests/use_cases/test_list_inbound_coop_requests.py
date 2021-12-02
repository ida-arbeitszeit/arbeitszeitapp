from datetime import datetime
from uuid import uuid4

from arbeitszeit.entities import Plan
from arbeitszeit.use_cases import (
    ListInboundCoopRequests,
    ListInboundCoopRequestsRequest,
    ListInboundCoopRequestsResponse,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import injection_test


def plan_in_list(plan: Plan, response: ListInboundCoopRequestsResponse) -> bool:
    for listed_request in response.cooperation_requests:
        if plan.id == listed_request.plan_id:
            return True
    return False


@injection_test
def test_emtpy_list_is_returned_when_cooperation_is_not_found(
    list_requests: ListInboundCoopRequests,
):
    response = list_requests(ListInboundCoopRequestsRequest(uuid4()))
    assert len(response.cooperation_requests) == 0


@injection_test
def test_empty_list_is_returned_when_there_are_no_requests_for_coordinator(
    list_requests: ListInboundCoopRequests,
    coop_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    coordinator = company_generator.create_company()
    coop = coop_generator.create_cooperation()
    plan_generator.create_plan(requested_cooperation=coop, activation_date=datetime.min)
    response = list_requests(ListInboundCoopRequestsRequest(coordinator.id))
    assert len(response.cooperation_requests) == 0


@injection_test
def test_correct_plans_are_returned_when_plans_request_cooperation(
    list_requests: ListInboundCoopRequests,
    coop_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    coordinator = company_generator.create_company()
    coop = coop_generator.create_cooperation(coordinator=coordinator)
    requesting_plan1 = plan_generator.create_plan(
        requested_cooperation=coop, activation_date=datetime.min
    )
    requesting_plan2 = plan_generator.create_plan(
        requested_cooperation=coop, activation_date=datetime.min
    )
    response = list_requests(ListInboundCoopRequestsRequest(coordinator.id))
    assert len(response.cooperation_requests) == 2
    assert plan_in_list(requesting_plan1, response)
    assert plan_in_list(requesting_plan2, response)
