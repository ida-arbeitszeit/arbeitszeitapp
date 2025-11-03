from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.services.account_details import AccountDetailsService, AccountTransfer


@dataclass
class GetMemberAccountResponse:
    transfers: list[AccountTransfer]
    balance: Decimal


@dataclass
class GetMemberAccountInteractor:
    database_gateway: DatabaseGateway
    account_details_service: AccountDetailsService

    def execute(self, member_id: UUID) -> GetMemberAccountResponse:
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        account = member.account
        transfers = self.account_details_service.get_account_transfers(account)
        account_balance = self.account_details_service.get_account_balance(account)
        return GetMemberAccountResponse(
            transfers=sorted(transfers, key=lambda t: t.date, reverse=True),
            balance=account_balance,
        )
