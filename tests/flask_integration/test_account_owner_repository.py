from arbeitszeit.entities import AccountTypes
from project.database.repositories import AccountingRepository, AccountOwnerRepository
from tests.data_generators import AccountGenerator, CompanyGenerator, MemberGenerator

from .dependency_injection import injection_test


@injection_test
def test_can_retrieve_owner_of_member_accounts(
    repository: AccountOwnerRepository,
    account_generator: AccountGenerator,
    member_generator: MemberGenerator,
) -> None:
    account = account_generator.create_account(AccountTypes.member)
    member = member_generator.create_member(account=account)
    assert repository.get_account_owner(account) == member


@injection_test
def test_can_retrieve_owner_of_company_accounts(
    repository: AccountOwnerRepository,
    account_generator: AccountGenerator,
    company_generator: CompanyGenerator,
) -> None:
    account = account_generator.create_account(AccountTypes.a)
    company = company_generator.create_company(labour_account=account)
    assert repository.get_account_owner(account) == company


@injection_test
def test_can_get_owner_of_public_account(
    repository: AccountOwnerRepository,
    social_accounting_repository: AccountingRepository,
) -> None:
    social_accounting = social_accounting_repository.get_or_create_social_accounting()
    assert repository.get_account_owner(social_accounting.account) == social_accounting
