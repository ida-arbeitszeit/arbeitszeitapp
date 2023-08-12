from uuid import uuid4

from arbeitszeit.records import Company, Plan
from arbeitszeit.use_cases.list_active_plans_of_company import (
    ListActivePlansOfCompany,
    ListPlansResponse,
)
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import injection_test


def plan_in_results(plan: Plan, response: ListPlansResponse) -> bool:
    return any(
        (
            plan.id == result.id and plan.prd_name == result.prd_name
            for result in response.plans
        )
    )


@injection_test
def test_list_plans_response_is_empty_for_nonexisting_company(
    list_plans: ListActivePlansOfCompany,
):
    response: ListPlansResponse = list_plans(company_id=uuid4())
    assert not response.plans


@injection_test
def test_list_plans_response_is_empty_for_company_without_plans(
    list_plans: ListActivePlansOfCompany,
    company_generator: CompanyGenerator,
):
    company: Company = company_generator.create_company_record()
    response: ListPlansResponse = list_plans(company_id=company.id)
    assert not response.plans


@injection_test
def test_list_plans_response_includes_single_plan(
    list_plans: ListActivePlansOfCompany,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan: Plan = plan_generator.create_plan(planner=company)
    response: ListPlansResponse = list_plans(company_id=company)
    assert plan_in_results(plan, response)


@injection_test
def test_list_plans_response_includes_multiple_plans(
    list_plans: ListActivePlansOfCompany,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan1: Plan = plan_generator.create_plan(planner=company)
    plan2: Plan = plan_generator.create_plan(planner=company)
    response: ListPlansResponse = list_plans(company_id=company)
    assert plan_in_results(plan1, response) and plan_in_results(plan2, response)
