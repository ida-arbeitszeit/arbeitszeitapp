from datetime import datetime

from arbeitszeit.use_cases import (
    CancelCooperationSolicitation,
    CancelCooperationSolicitationRequest,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_that_false_is_returned_when_requester_is_not_planner(
    use_case: CancelCooperationSolicitation,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    plan = plan_generator.create_plan()
    company = company_generator.create_company_entity()
    response = use_case(CancelCooperationSolicitationRequest(company.id, plan.id))
    assert response == False


@injection_test
def test_that_false_is_returned_when_plan_has_no_pending_requests(
    use_case: CancelCooperationSolicitation,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    company = company_generator.create_company()
    plan = plan_generator.create_plan(planner=company)
    response = use_case(CancelCooperationSolicitationRequest(company, plan.id))
    assert response == False


@injection_test
def test_that_true_is_returned_when_coop_request_gets_canceled(
    use_case: CancelCooperationSolicitation,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
    coop_generator: CooperationGenerator,
):
    coop = coop_generator.create_cooperation()
    company = company_generator.create_company()
    plan = plan_generator.create_plan(
        planner=company, activation_date=datetime.min, requested_cooperation=coop
    )
    assert plan.requested_cooperation is not None
    response = use_case(CancelCooperationSolicitationRequest(company, plan.id))
    assert response == True
    assert plan.requested_cooperation is None
