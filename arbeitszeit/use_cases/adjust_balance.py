from decimal import Decimal

from arbeitszeit.entities import Account


def adjust_balance(account: Account, amount: Decimal) -> Account:
    """changes the balance of specified accounts."""
    account.change_credit(amount)
    return account
