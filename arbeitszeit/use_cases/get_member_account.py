from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Union
from uuid import UUID

from arbeitszeit.entities import Company, Member, SocialAccounting, Transaction
from arbeitszeit.repositories import (
    AccountOwnerRepository,
    AccountRepository,
    MemberRepository,
)
from arbeitszeit.transactions import TransactionTypes, UserAccountingService

User = Union[Member, Company]
UserOrSocialAccounting = Union[User, SocialAccounting]


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
    member_repository: MemberRepository
    acount_owner_repository: AccountOwnerRepository
    account_repository: AccountRepository

    def __call__(self, member_id: UUID) -> GetMemberAccountResponse:
        member = self.member_repository.get_members().with_id(member_id).first()
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
        balance = self.account_repository.get_account_balance(member.account)
        return GetMemberAccountResponse(transaction_info, balance)

    def _get_peer_name(self, user: Member, transaction: Transaction) -> str:
        user_is_sender = self.accounting_service.user_is_sender(transaction, user)
        if user_is_sender:
            receiving_account = (
                self.account_repository.get_accounts()
                .with_id(transaction.receiving_account)
                .first()
            )
            assert receiving_account
            receiver = self.acount_owner_repository.get_account_owner(
                receiving_account.id
            )
            return receiver.get_name()
        else:
            sending_account = (
                self.account_repository.get_accounts()
                .with_id(transaction.sending_account)
                .first()
            )
            assert sending_account
            sender = self.acount_owner_repository.get_account_owner(sending_account.id)
            return sender.get_name()
