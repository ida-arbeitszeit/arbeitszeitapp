from project.database.repositories import AccountRepository
from tests.data_generators import AccountGenerator

from .dependency_injection import injection_test


@injection_test
def test_the_account_balance_of_newly_created_accounts_is_0(
    repository: AccountRepository,
    generator: AccountGenerator,
) -> None:
    account = generator.create_account()
    assert repository.get_account_balance(account) == 0
