from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.entities import AccountOwner, Member, Transaction
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transactions import TransactionTypes, UserAccountingService


@dataclass
class TransactionInfo:
    date: datetime
    peer_name: str
    transaction_volume: Decimal
    purpose: str
    type: TransactionTypes


@dataclass
class GetMemberAccountResponse:
    transactions: List[TransactionInfo]
    balance: Decimal


@dataclass
class GetMemberAccount:
    accounting_service: UserAccountingService
    database: DatabaseGateway

    def __call__(self, member_id: UUID) -> GetMemberAccountResponse:
        member = self.database.get_members().with_id(member_id).first()
        assert member
        transaction_info = [
            TransactionInfo(
                date=row.transaction.date,
                peer_name=self._get_peer_name(member, row.transaction),
                transaction_volume=row.volume,
                purpose=row.transaction.purpose,
                type=row.transaction_type,
            )
            for row in self.accounting_service.get_statement_of_account(
                member, member.accounts()
            )
        ]
        result = (
            self.database.get_accounts()
            .with_id(member.account)
            .joined_with_balance()
            .first()
        )
        assert result
        balance = result[1]
        return GetMemberAccountResponse(transaction_info, balance)

    def _get_peer_name(self, user: Member, transaction: Transaction) -> str:
        user_is_sender = self.accounting_service.user_is_sender(transaction, user)
        if user_is_sender:
            return self.get_account_owner(transaction.receiving_account).get_name()
        else:
            return self.get_account_owner(transaction.sending_account).get_name()

    def get_account_owner(self, account_id: UUID) -> AccountOwner:
        result = (
            self.database.get_accounts().with_id(account_id).joined_with_owner().first()
        )
        assert result
        _, owner = result
        return owner
