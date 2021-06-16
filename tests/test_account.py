from arbeitszeit.use_cases import adjust_balance
from tests.data_generators import AccountGenerator
from tests.dependency_injection import injection_test


@injection_test
def test_account_balance_changes(
    account_generator: AccountGenerator,
):
    account = account_generator.create_account()
    adjust_balance(account, -5)
    assert account.balance == -5
