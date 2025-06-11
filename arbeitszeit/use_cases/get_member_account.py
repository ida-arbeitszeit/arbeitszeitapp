from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers import TransferType


@dataclass
class TransferInfo:
    date: datetime
    peer_name: str
    transferred_value: Decimal
    type: TransferType


@dataclass
class GetMemberAccountResponse:
    transfers: List[TransferInfo]
    balance: Decimal


@dataclass
class GetMemberAccount:
    database: DatabaseGateway

    def __call__(self, member_id: UUID) -> GetMemberAccountResponse:
        member = self.database.get_members().with_id(member_id).first()
        assert member
        transfer_info: List[TransferInfo] = []
        work_certificate_transfers = (
            self.database.get_transfers()
            .where_account_is_creditor(member.account)
            .joined_with_debtor()
        )
        consumption_or_tax_transfers = (
            self.database.get_transfers()
            .where_account_is_debtor(member.account)
            .joined_with_creditor()
        )
        for tf, debtor in work_certificate_transfers:
            transfer_info.append(
                TransferInfo(
                    date=tf.date,
                    peer_name=debtor.get_name(),
                    transferred_value=tf.value,
                    type=TransferType.work_certificates,
                )
            )
        for tf, creditor in consumption_or_tax_transfers:
            transfer_info.append(
                TransferInfo(
                    date=tf.date,
                    peer_name=creditor.get_name(),
                    transferred_value=-tf.value,  # negative value for consumption or tax
                    type=tf.type,
                )
            )
        transfer_info.sort(key=lambda t: t.date, reverse=True)
        return GetMemberAccountResponse(
            transfers=transfer_info, balance=self.get_account_balance(member.account)
        )

    def get_account_balance(self, account: UUID) -> Decimal:
        result = (
            self.database.get_accounts().with_id(account).joined_with_balance().first()
        )
        assert result
        return result[1]
