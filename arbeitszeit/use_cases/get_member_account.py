from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers import TransferType


@dataclass
class TransactionInfo:
    date: datetime
    peer_name: str
    transaction_volume: Decimal
    purpose: str
    type: TransferType


@dataclass
class GetMemberAccountResponse:
    transactions: List[TransactionInfo]
    balance: Decimal


@dataclass
class GetMemberAccount:
    database: DatabaseGateway

    def __call__(self, member_id: UUID) -> GetMemberAccountResponse:
        member = self.database.get_members().with_id(member_id).first()
        assert member
        transaction_info: List[TransactionInfo] = []
        transactions_of_consumption_and_receiver = (
            self.database.get_transactions()
            .where_account_is_sender(member.account)
            .joined_with_receiver()
        )
        transfers_of_work_certificates_and_debtor = (
            self.database.get_transfers()
            .where_account_is_creditor(member.account)
            .joined_with_debtor()
        )
        transfers_of_taxes_and_creditor = (
            self.database.get_transfers()
            .where_account_is_debtor(member.account)
            .joined_with_creditor()
        )
        for tx, receiver in transactions_of_consumption_and_receiver:
            transaction_info.append(
                TransactionInfo(
                    date=tx.date,
                    peer_name=receiver.get_name(),
                    transaction_volume=-tx.amount_sent,  # negative value
                    purpose=tx.purpose,
                    type=TransferType.private_consumption,
                )
            )
        for tf, debtor in transfers_of_work_certificates_and_debtor:
            transaction_info.append(
                TransactionInfo(
                    date=tf.date,
                    peer_name=debtor.get_name(),
                    transaction_volume=tf.value,
                    purpose="",
                    type=TransferType.work_certificates,
                )
            )
        for tf, creditor in transfers_of_taxes_and_creditor:
            transaction_info.append(
                TransactionInfo(
                    date=tf.date,
                    peer_name=creditor.get_name(),
                    transaction_volume=-tf.value,  # negative value
                    purpose="",
                    type=TransferType.taxes,
                )
            )
        transaction_info.sort(key=lambda t: t.date, reverse=True)
        result = (
            self.database.get_accounts()
            .with_id(member.account)
            .joined_with_balance()
            .first()
        )
        assert result
        balance = result[1]
        return GetMemberAccountResponse(transaction_info, balance)
