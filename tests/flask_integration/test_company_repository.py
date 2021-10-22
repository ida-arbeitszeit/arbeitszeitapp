from typing import List
from uuid import uuid4

from pytest import raises
from sqlalchemy.exc import IntegrityError

from arbeitszeit.entities import AccountTypes, Company
from project.database.repositories import AccountRepository, CompanyRepository
from tests.data_generators import CompanyGenerator

from .dependency_injection import injection_test


def company_in_companies(company: Company, companies: List[Company]) -> bool:
    return company.id in [c.id for c in companies]


@injection_test
def test_company_repository_can_convert_to_and_from_orm_without_changing_the_object(
    company_generator: CompanyGenerator,
    company_repository: CompanyRepository,
):
    expected_company = company_generator.create_company()
    actual_company = company_repository.object_from_orm(
        company_repository.object_to_orm(
            expected_company,
        )
    )
    assert actual_company == expected_company


@injection_test
def test_cannot_retrieve_company_from_arbitrary_uuid(
    company_repository: CompanyRepository,
):
    assert company_repository.get_by_id(uuid4()) is None


@injection_test
def test_can_retrieve_a_company_by_its_uuid(
    company_generator: CompanyGenerator,
    company_repository: CompanyRepository,
):
    company = company_generator.create_company()
    assert company_repository.get_by_id(company.id) == company


@injection_test
def test_can_create_company_with_correct_name(
    company_repository: CompanyRepository,
    account_repository: AccountRepository,
):
    means_account = account_repository.create_account(AccountTypes.p)
    labour_account = account_repository.create_account(AccountTypes.a)
    resource_account = account_repository.create_account(AccountTypes.r)
    products_account = account_repository.create_account(AccountTypes.prd)
    expected_name = "Rosa"
    company = company_repository.create_company(
        email="rosa@cp.org",
        name=expected_name,
        password="testpassword",
        means_account=means_account,
        labour_account=labour_account,
        resource_account=resource_account,
        products_account=products_account,
    )
    assert company.name == expected_name


@injection_test
def test_can_detect_if_company_with_email_is_already_present(
    company_generator: CompanyGenerator,
    company_repository: CompanyRepository,
):
    expected_email = "rosa@cp.org"
    assert not company_repository.has_company_with_email(expected_email)
    company_generator.create_company(email=expected_email)
    assert company_repository.has_company_with_email(expected_email)


@injection_test
def test_count_no_registered_company_if_none_was_created(
    repository: CompanyRepository,
) -> None:
    assert repository.count_registered_companies() == 0


@injection_test
def test_count_one_registered_company_if_one_was_created(
    repository: CompanyRepository,
    generator: CompanyGenerator,
) -> None:
    generator.create_company()
    assert repository.count_registered_companies() == 1


@injection_test
def test_that_can_not_register_company_with_same_email_twice(
    repository: CompanyRepository,
    generator: CompanyGenerator,
):
    with raises(IntegrityError):
        generator.create_company(email="company@provider.de")
        generator.create_company(email="company@provider.de")


@injection_test
def test_that_get_all_companies_returns_all_companies(
    repository: CompanyRepository,
    generator: CompanyGenerator,
):
    expected_company1 = generator.create_company(email="company1@provider.de")
    expected_company2 = generator.create_company(email="company2@provider.de")
    all_companies = list(repository.get_all_companies())
    assert company_in_companies(expected_company1, all_companies)
    assert company_in_companies(expected_company2, all_companies)


@injection_test
def test_query_companies_by_name_matching_exactly(
    repository: CompanyRepository,
    generator: CompanyGenerator,
):
    expected_company = generator.create_company(
        name="Company1", email="company1@provider.de"
    )
    unexpected_company = generator.create_company(
        name="Company2", email="company2@provider.de"
    )
    companies_by_name = list(repository.query_companies_by_name("Company1"))
    assert company_in_companies(expected_company, companies_by_name)
    assert not company_in_companies(unexpected_company, companies_by_name)


@injection_test
def test_query_companies_by_name_with_matching_substring(
    repository: CompanyRepository,
    generator: CompanyGenerator,
):
    expected_company = generator.create_company(
        name="Company One", email="company1@provider.de"
    )
    unexpected_company = generator.create_company(
        name="Company Two", email="company2@provider.de"
    )
    companies_by_name = list(repository.query_companies_by_name("One"))
    assert company_in_companies(expected_company, companies_by_name)
    assert not company_in_companies(unexpected_company, companies_by_name)


@injection_test
def test_query_companies_by_name_with_capitalization(
    repository: CompanyRepository,
    generator: CompanyGenerator,
):
    expected_company = generator.create_company(
        name="COMPANY", email="company@provider.de"
    )
    companies_result = list(repository.query_companies_by_name("company"))
    assert company_in_companies(expected_company, companies_result)


@injection_test
def test_query_companies_by_email_matching_exactly(
    repository: CompanyRepository,
    generator: CompanyGenerator,
):
    expected_company = generator.create_company(email="company1@provider.de")
    unexpected_company = generator.create_company(email="company2@provider.de")
    companies_by_email = list(
        repository.query_companies_by_email("company1@provider.de")
    )
    assert company_in_companies(expected_company, companies_by_email)
    assert not company_in_companies(unexpected_company, companies_by_email)


@injection_test
def test_query_companies_by_email_with_matching_substring(
    repository: CompanyRepository,
    generator: CompanyGenerator,
):
    expected_company = generator.create_company(email="company.one@provider.de")
    unexpected_company = generator.create_company(email="company.two@provider.de")
    companies_by_email = list(repository.query_companies_by_email("one"))
    assert company_in_companies(expected_company, companies_by_email)
    assert not company_in_companies(unexpected_company, companies_by_email)


@injection_test
def test_query_companies_by_email_with_capitalization(
    repository: CompanyRepository,
    generator: CompanyGenerator,
):
    expected_company = generator.create_company(email="company@provider.de")
    companies_result = list(repository.query_companies_by_email("COMPANY"))
    assert company_in_companies(expected_company, companies_result)
