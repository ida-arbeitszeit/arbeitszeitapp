from datetime import datetime

from arbeitszeit.use_cases import GetMemberDashboard
from tests.data_generators import CompanyGenerator, MemberGenerator, PlanGenerator

from .dependency_injection import injection_test
from .repositories import CompanyWorkerRepository


@injection_test
def test_that_correct_workplace_email_is_shown(
    get_member_dashboard: GetMemberDashboard,
    company_worker_repository: CompanyWorkerRepository,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    worker = member_generator.create_member()
    workplace = company_generator.create_company(email="companyname@mail.com")
    company_worker_repository.add_worker_to_company(workplace, worker)

    member_info = get_member_dashboard(worker.id)
    assert member_info.workplaces[0].workplace_email == "companyname@mail.com"


@injection_test
def test_that_correct_workplace_name_is_shown(
    get_member_dashboard: GetMemberDashboard,
    company_worker_repository: CompanyWorkerRepository,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    worker = member_generator.create_member()
    workplace = company_generator.create_company(name="SomeCompanyNameXY")
    company_worker_repository.add_worker_to_company(workplace, worker)

    member_info = get_member_dashboard(worker.id)
    assert member_info.workplaces[0].workplace_name == "SomeCompanyNameXY"


@injection_test
def test_that_three_latest_plans_is_empty_if_there_are_no_plans(
    get_member_dashboard: GetMemberDashboard,
    member_generator: MemberGenerator,
):
    member = member_generator.create_member()
    response = get_member_dashboard(member.id)
    assert not response.three_latest_plans


@injection_test
def test_three_latest_plans_has_at_least_one_entry_if_there_is_one_active_plan(
    get_member_dashboard: GetMemberDashboard,
    member_generator: MemberGenerator,
    plan_generator: PlanGenerator,
):
    plan_generator.create_plan(activation_date=datetime.min)
    member = member_generator.create_member()
    response = get_member_dashboard(member.id)
    assert response.three_latest_plans
