from uuid import uuid4

import pytest

from arbeitszeit.entities import AccountTypes
from project.database.repositories import AccountRepository, CompanyRepository
from project.error import CompanyNotFound
from tests.data_generators import CompanyGenerator

from .dependency_injection import injection_test


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
def test_cannot_retriev_company_from_arbitrary_uuid(
    company_repository: CompanyRepository,
):
    with pytest.raises(CompanyNotFound):
        company_repository.get_by_id(uuid4())


@injection_test
def test_can_retriev_a_company_by_its_uuid(
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
