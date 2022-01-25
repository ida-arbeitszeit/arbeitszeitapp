from datetime import datetime
from uuid import uuid4

from arbeitszeit.use_cases import GetCompanySummary
from arbeitszeit.use_cases.get_company_summary import PlanDetails
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_returns_nothing_when_company_does_not_exist(
    get_company_summary: GetCompanySummary,
):
    response = get_company_summary(uuid4())
    assert response is None


@injection_test
def test_returns_name(
    get_company_summary: GetCompanySummary, company_generator: CompanyGenerator
):
    company = company_generator.create_company(name="Company XYZ")
    response = get_company_summary(company.id)
    assert response
    assert response.name == "Company XYZ"


@injection_test
def test_returns_email(
    get_company_summary: GetCompanySummary, company_repository: CompanyGenerator
):
    company = company_repository.create_company(email="company@cp.org")
    response = get_company_summary(company.id)
    assert response
    assert response.email == "company@cp.org"


@injection_test
def test_returns_register_date(
    get_company_summary: GetCompanySummary, company_repository: CompanyGenerator
):
    company = company_repository.create_company(registered_on=datetime(2022, 1, 25))
    response = get_company_summary(company.id)
    assert response
    assert response.registered_on == datetime(2022, 1, 25)


@injection_test
def test_returns_empty_list_of_companys_active_plans_when_there_are_none(
    get_company_summary: GetCompanySummary,
    company_repository: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_repository.create_company()
    plan_generator.create_plan(planner=company, activation_date=None)
    response = get_company_summary(company.id)
    assert response
    assert response.active_plans == []


@injection_test
def test_returns_list_of_companys_active_plans_when_there_are_any(
    get_company_summary: GetCompanySummary,
    company_repository: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_repository.create_company()
    plan1 = plan_generator.create_plan(planner=company, activation_date=datetime.min)
    plan2 = plan_generator.create_plan(planner=company, activation_date=datetime.min)
    response = get_company_summary(company.id)
    assert response
    assert response.active_plans == [
        PlanDetails(plan1.id, plan1.prd_name),
        PlanDetails(plan2.id, plan2.prd_name),
    ]


@injection_test
def test_returns_list_of_companys_active_plans_and_ignores_inactive_plans(
    get_company_summary: GetCompanySummary,
    company_repository: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_repository.create_company()
    plan_generator.create_plan(planner=company, activation_date=datetime.min)
    plan_generator.create_plan(planner=company, activation_date=datetime.min)
    plan_generator.create_plan(planner=company, activation_date=None)
    response = get_company_summary(company.id)
    assert response
    assert len(response.active_plans) == 2
