from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers import TransferType


@dataclass
class TransferInfo:
    date: datetime
    peer_name: str
    transferred_value: Decimal
    type: TransferType
    is_debit_transfer: bool


@dataclass
class GetMemberAccountResponse:
    transfers: list[TransferInfo]
    balance: Decimal


@dataclass
class GetMemberAccountInteractor:
    database_gateway: DatabaseGateway

    def execute(self, member_id: UUID) -> GetMemberAccountResponse:
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        transfers = self._get_account_transfers(member.account)
        transfers.sort(key=lambda t: t.date, reverse=True)
        return GetMemberAccountResponse(
            transfers=transfers, balance=self._get_account_balance(member.account)
        )

    def _get_account_transfers(self, account: UUID) -> list[TransferInfo]:
        transfers: list[TransferInfo] = []
        for transfer, debtor, creditor in (
            self.database_gateway.get_transfers()
            .where_account_is_debtor_or_creditor(account)
            .joined_with_debtor_and_creditor()
        ):
            is_debit_transfer = transfer.debit_account == account
            peer_name = creditor.get_name() if is_debit_transfer else debtor.get_name()
            value = -transfer.value if is_debit_transfer else transfer.value
            transfers.append(
                TransferInfo(
                    date=transfer.date,
                    peer_name=peer_name,
                    transferred_value=value,
                    type=transfer.type,
                    is_debit_transfer=is_debit_transfer,
                )
            )
        return transfers

    def _get_account_balance(self, account: UUID) -> Decimal:
        result = (
            self.database_gateway.get_accounts()
            .with_id(account)
            .joined_with_balance()
            .first()
        )
        assert result
        return result[1]
