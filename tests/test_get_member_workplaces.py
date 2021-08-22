from arbeitszeit.use_cases import GetMemberWorkplaces
from tests.data_generators import CompanyGenerator, MemberGenerator
from tests.dependency_injection import injection_test
from tests.repositories import CompanyWorkerRepository


@injection_test
def test_that_correct_workplace_email_is_shown(
    get_member_workplaces: GetMemberWorkplaces,
    company_worker_repository: CompanyWorkerRepository,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    worker = member_generator.create_member()
    workplace = company_generator.create_company(email="companyname@mail.com")
    company_worker_repository.add_worker_to_company(workplace, worker)

    workplaces = get_member_workplaces(worker)
    assert workplaces[0].workplace_email == "companyname@mail.com"


@injection_test
def test_that_correct_workplace_name_is_shown(
    get_member_workplaces: GetMemberWorkplaces,
    company_worker_repository: CompanyWorkerRepository,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    worker = member_generator.create_member()
    workplace = company_generator.create_company(name="SomeCompanyNameXY")
    company_worker_repository.add_worker_to_company(workplace, worker)

    workplaces = get_member_workplaces(worker)
    assert workplaces[0].workplace_name == "SomeCompanyNameXY"
