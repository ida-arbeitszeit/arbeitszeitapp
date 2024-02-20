from dataclasses import dataclass
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ShowCompanyAccountsRequest:
    company: UUID


@dataclass
class ShowCompanyAccountsResponse:
    balances: List[Decimal]


@dataclass
class ShowCompanyAccounts:
    database: DatabaseGateway

    def __call__(
        self, request: ShowCompanyAccountsRequest
    ) -> ShowCompanyAccountsResponse:
        accounts = dict(
            (account.id, balance)
            for account, balance in self.database.get_accounts()
            .owned_by_company(request.company)
            .joined_with_balance()
        )
        company = self.database.get_companies().with_id(request.company).first()
        assert company
        balances = [
            accounts[company.means_account],
            accounts[company.raw_material_account],
            accounts[company.work_account],
            accounts[company.product_account],
        ]
        return ShowCompanyAccountsResponse(balances=balances)
