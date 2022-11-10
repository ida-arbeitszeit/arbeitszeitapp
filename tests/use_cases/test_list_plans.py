from datetime import datetime
from uuid import uuid4

from arbeitszeit.entities import Company, Plan
from arbeitszeit.use_cases import ListPlans, ListPlansResponse
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
    list_plans: ListPlans,
):
    response: ListPlansResponse = list_plans(company_id=uuid4())
    assert not response.plans


@injection_test
def test_list_plans_response_is_empty_for_company_without_plans(
    list_plans: ListPlans,
    company_generator: CompanyGenerator,
):
    company: Company = company_generator.create_company_entity()
    response: ListPlansResponse = list_plans(company_id=company.id)
    assert not response.plans


@injection_test
def test_list_plans_response_includes_single_plan(
    list_plans: ListPlans,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company: Company = company_generator.create_company_entity()
    plan: Plan = plan_generator.create_plan(
        planner=company, activation_date=datetime.min
    )
    response: ListPlansResponse = list_plans(company_id=company.id)
    assert plan_in_results(plan, response)


@injection_test
def test_list_plans_response_includes_multiple_plans(
    list_plans: ListPlans,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company: Company = company_generator.create_company_entity()
    plan1: Plan = plan_generator.create_plan(
        planner=company, activation_date=datetime.min
    )
    plan2: Plan = plan_generator.create_plan(
        planner=company, activation_date=datetime.min
    )
    response: ListPlansResponse = list_plans(company_id=company.id)
    assert plan_in_results(plan1, response) and plan_in_results(plan2, response)
