from dataclasses import dataclass
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.repositories import AccountRepository, DatabaseGateway


@dataclass
class ShowMyAccountsRequest:
    current_user: UUID


@dataclass
class ShowMyAccountsResponse:
    balances: List[Decimal]


@dataclass
class ShowMyAccounts:
    database: DatabaseGateway
    account_repository: AccountRepository

    def __call__(self, request: ShowMyAccountsRequest) -> ShowMyAccountsResponse:
        company = self.database.get_companies().with_id(request.current_user).first()
        assert company
        balances = [
            self.account_repository.get_account_balance(account)
            for account in company.accounts()
        ]
        return ShowMyAccountsResponse(balances=balances)
