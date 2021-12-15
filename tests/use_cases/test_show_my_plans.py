from uuid import uuid4

from arbeitszeit.use_cases import ShowMyPlansRequest, ShowMyPlansUseCase

from ..data_generators import CompanyGenerator, PlanGenerator
from .dependency_injection import injection_test


@injection_test
def test_that_no_plans_are_returned_when_no_plans_were_created(
    use_case: ShowMyPlansUseCase,
):
    response = use_case(request=ShowMyPlansRequest(company_id=uuid4()))
    assert not response.count_all_plans


@injection_test
def test_that_one_approved_plan_is_returned_after_one_plan_was_created(
    use_case: ShowMyPlansUseCase,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    company = company_generator.create_company()
    plan_generator.create_plan(planner=company)
    response = use_case(request=ShowMyPlansRequest(company_id=company.id))
    assert response.count_all_plans == 1


@injection_test
def test_that_no_plans_for_a_company_without_plans_are_found(
    use_case: ShowMyPlansUseCase,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    company = company_generator.create_company()
    other_company = company_generator.create_company()
    plan_generator.create_plan(approved=True, planner=company)
    response = use_case(request=ShowMyPlansRequest(company_id=other_company.id))
    assert not response.count_all_plans
