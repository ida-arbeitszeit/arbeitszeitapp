import pytest

from arbeitszeit.errors import CompanyAlreadyExists
from arbeitszeit.use_cases import RegisterCompany

from .dependency_injection import injection_test
from .repositories import AccountRepository


@injection_test
def test_that_registering_a_company_does_create_a_company_account(
    register_company: RegisterCompany, account_repository: AccountRepository
) -> None:
    new_company = register_company("a_company@company.org", "ACompany", "testpassword")
    for account in new_company.accounts():
        assert account in account_repository


@injection_test
def test_that_cannot_register_user_with_same_email_twice(
    register_company: RegisterCompany,
):
    email = "betrieb@cp.org"
    register_company(email, "Betrieb1", "testpassword")
    with pytest.raises(CompanyAlreadyExists):
        register_company(email, "Betrieb2", "other_password")
