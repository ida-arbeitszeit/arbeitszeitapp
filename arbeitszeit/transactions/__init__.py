from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Union
from uuid import UUID

from arbeitszeit.records import AccountOwner, AccountTypes, Company, Member, Transaction
from arbeitszeit.repositories import DatabaseGateway

from .transaction_type import TransactionTypes


@dataclass
class AccountStatementRow:
    transaction: Transaction
    volume: Decimal
    transaction_type: TransactionTypes
    account_type: AccountTypes
    peer: AccountOwner


@dataclass
class UserAccountingService:
    database_gateway: DatabaseGateway

    def get_statement_of_account(
        self, user: Union[Member, Company], accounts: Iterable[UUID]
    ) -> Iterable[AccountStatementRow]:
        accounts = set(accounts) & set(user.accounts())
        transactions = (
            self.database_gateway.get_transactions()
            .where_account_is_sender_or_receiver(*accounts)
            .ordered_by_transaction_date(descending=True)
        )
        for (
            transaction,
            sender,
            receiver,
        ) in transactions.joined_with_sender_and_receiver():
            user_is_sender = transaction.sending_account in accounts
            account_type = user.get_account_type(
                transaction.sending_account
                if user_is_sender
                else transaction.receiving_account
            )
            assert account_type
            peer = receiver if user_is_sender else sender
            sending_account_type = sender.get_account_type(transaction.sending_account)
            assert sending_account_type
            receiving_account_type = receiver.get_account_type(
                transaction.receiving_account
            )
            assert receiving_account_type
            yield AccountStatementRow(
                transaction=transaction,
                volume=-transaction.amount_sent
                if user_is_sender
                else transaction.amount_received,
                transaction_type=self._get_transaction_type(
                    user_is_sender=user_is_sender,
                    sending_account=sending_account_type,
                    receiving_account=receiving_account_type,
                ),
                account_type=account_type,
                peer=peer,
            )

    def _get_transaction_type(
        self,
        sending_account: AccountTypes,
        receiving_account: AccountTypes,
        user_is_sender: bool,
    ) -> TransactionTypes:
        if user_is_sender:
            transaction_type = TransactionTypes.for_sender(
                sender=sending_account, receiver=receiving_account
            )
        else:
            transaction_type = TransactionTypes.for_receiver(
                sender=sending_account, receiver=receiving_account
            )
        assert transaction_type
        return transaction_type
