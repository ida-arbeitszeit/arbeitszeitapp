from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Union
from uuid import UUID

from injector import inject

from arbeitszeit.entities import (
    AccountTypes,
    Company,
    Member,
    SocialAccounting,
    Transaction,
)
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


@inject
@dataclass
class GetMemberAccount:
    accounting_service: UserAccountingService
    member_repository: MemberRepository
    acount_owner_repository: AccountOwnerRepository
    account_repository: AccountRepository

    def __call__(self, member_id: UUID) -> GetMemberAccountResponse:
        member = self.member_repository.get_by_id(member_id)
        assert member
        transaction_info = [
            self._create_info(member, transaction)
            for transaction in self.accounting_service.get_account_transactions_sorted(
                member, AccountTypes.member
            )
        ]
        balance = self.account_repository.get_account_balance(member.account)
        return GetMemberAccountResponse(transaction_info, balance)

    def _create_info(
        self,
        user: Member,
        transaction: Transaction,
    ) -> TransactionInfo:
        sender = self.acount_owner_repository.get_account_owner(
            transaction.sending_account
        )
        receiver = self.acount_owner_repository.get_account_owner(
            transaction.receiving_account
        )
        user_is_sender = self.accounting_service.user_is_sender(transaction, user)
        peer_name = self._get_peer_name(user_is_sender, sender, receiver)
        transaction_volume = self.accounting_service.get_transaction_volume(
            transaction, user_is_sender
        )
        return TransactionInfo(
            date=transaction.date,
            peer_name=peer_name,
            transaction_volume=transaction_volume,
            purpose=transaction.purpose,
            type=self.accounting_service.get_transaction_type(
                transaction, user_is_sender
            ),
        )

    def _get_peer_name(
        self,
        user_is_sender: bool,
        sender: UserOrSocialAccounting,
        receiver: UserOrSocialAccounting,
    ) -> str:
        if user_is_sender:
            return receiver.get_name()
        else:
            return sender.get_name()
