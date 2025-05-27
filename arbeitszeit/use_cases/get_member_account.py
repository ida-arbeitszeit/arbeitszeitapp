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
    transfer_value: Decimal
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
        transfers_of_work_certificates_and_debtor = (
            self.database.get_transfers()
            .where_account_is_creditor(member.account)
            .joined_with_debtor()
        )
        transfers_of_consumptions_and_taxes_joined_with_creditor = (
            self.database.get_transfers()
            .where_account_is_debtor(member.account)
            .joined_with_creditor()
        )
        for tf, debtor in transfers_of_work_certificates_and_debtor:
            transfer_info.append(
                TransferInfo(
                    date=tf.date,
                    peer_name=debtor.get_name(),
                    transfer_value=tf.value,
                    type=TransferType.work_certificates,
                )
            )
        for tf, creditor in transfers_of_consumptions_and_taxes_joined_with_creditor:
            if tf.type == TransferType.private_consumption:
                transfer_info.append(
                    TransferInfo(
                        date=tf.date,
                        peer_name=creditor.get_name(),
                        transfer_value=-tf.value,  # negative value
                        type=TransferType.private_consumption,
                    )
                )
            elif tf.type == TransferType.taxes:
                transfer_info.append(
                    TransferInfo(
                        date=tf.date,
                        peer_name=creditor.get_name(),
                        transfer_value=-tf.value,  # negative value
                        type=TransferType.taxes,
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
