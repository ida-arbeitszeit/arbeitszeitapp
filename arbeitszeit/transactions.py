from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import Iterable, List, Union
from uuid import UUID

from .entities import (
    AccountOwner,
    AccountTypes,
    Company,
    Member,
    SocialAccounting,
    Transaction,
)
from .repositories import DatabaseGateway


class TransactionTypes(Enum):
    """
    'Subjective' transaction types, i.e. seen from a concrete user perspective.
    """

    credit_for_wages = auto()
    payment_of_wages = auto()
    incoming_wages = auto()
    credit_for_fixed_means = auto()
    payment_of_fixed_means = auto()
    credit_for_liquid_means = auto()
    payment_of_liquid_means = auto()
    expected_sales = auto()
    sale_of_consumer_product = auto()
    payment_of_consumer_product = auto()
    sale_of_fixed_means = auto()
    sale_of_liquid_means = auto()


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

    def get_all_transactions_sorted(
        self, user: Union[Member, Company]
    ) -> List[Transaction]:
        return list(
            self.database_gateway.get_transactions()
            .where_account_is_sender_or_receiver(*user.accounts())
            .ordered_by_transaction_date(descending=True)
        )

    def get_account_transactions_sorted(
        self, user: Union[Member, Company], queried_account_type: AccountTypes
    ) -> List[Transaction]:
        account = user.get_account_by_type(queried_account_type)
        if account is None:
            return []
        else:
            return list(
                self.database_gateway.get_transactions()
                .where_account_is_sender_or_receiver(account)
                .ordered_by_transaction_date(descending=True)
            )

    def user_is_sender(
        self, transaction: Transaction, user: Union[Member, Company]
    ) -> bool:
        return transaction.sending_account in user.accounts()

    def _get_transaction_type(
        self,
        transaction: Transaction,
        sender: AccountOwner,
        receiver: AccountOwner,
        user_is_sender: bool,
    ) -> TransactionTypes:
        """
        Based on wether the user is sender or receiver,
        this method returns the 'subjective' transaction type.
        """
        sending_account = sender.get_account_type(transaction.sending_account)
        assert sending_account
        receiving_account = receiver.get_account_type(transaction.receiving_account)
        assert receiving_account
        if user_is_sender:
            if sending_account == AccountTypes.a:
                transaction_type = TransactionTypes.payment_of_wages
            elif sending_account == AccountTypes.p:
                transaction_type = TransactionTypes.payment_of_fixed_means
            elif sending_account == AccountTypes.r:
                transaction_type = TransactionTypes.payment_of_liquid_means
            elif sending_account == AccountTypes.member:
                transaction_type = TransactionTypes.payment_of_consumer_product
        else:
            if sending_account == AccountTypes.accounting:
                if receiving_account == AccountTypes.a:
                    transaction_type = TransactionTypes.credit_for_wages
                elif receiving_account == AccountTypes.p:
                    transaction_type = TransactionTypes.credit_for_fixed_means
                elif receiving_account == AccountTypes.r:
                    transaction_type = TransactionTypes.credit_for_liquid_means
                elif receiving_account == AccountTypes.prd:
                    transaction_type = TransactionTypes.expected_sales
                elif receiving_account == AccountTypes.member:
                    transaction_type = TransactionTypes.incoming_wages
            elif sending_account == AccountTypes.p:
                transaction_type = TransactionTypes.sale_of_fixed_means
            elif sending_account == AccountTypes.r:
                transaction_type = TransactionTypes.sale_of_liquid_means
            elif sending_account == AccountTypes.a:
                transaction_type = TransactionTypes.incoming_wages
            elif sending_account == AccountTypes.member:
                transaction_type = TransactionTypes.sale_of_consumer_product
        assert transaction_type
        return transaction_type

    def get_transaction_volume(
        self,
        transaction: Transaction,
        user_is_sender: bool,
    ) -> Decimal:
        """
        Based on wether the user is sender or receiver,
        this method returns the 'subjective' transaction volume.
        """
        if user_is_sender:
            if transaction.amount_sent == 0:
                return Decimal(0)
            return -1 * transaction.amount_sent
        return transaction.amount_received

    def get_buyer(
        self,
        transaction_type: TransactionTypes,
        transaction: Transaction,
    ) -> Union[Member, Company, None]:
        if transaction_type not in (
            TransactionTypes.sale_of_consumer_product,
            TransactionTypes.sale_of_fixed_means,
            TransactionTypes.sale_of_liquid_means,
        ):
            return None
        buyer_account = (
            self.database_gateway.get_accounts()
            .with_id(transaction.sending_account)
            .first()
        )
        assert buyer_account
        buyer = self._get_account_owner(buyer_account.id)
        assert not isinstance(
            buyer, SocialAccounting
        )  # from the transactiontype we know: buyer can't be social accounting
        return buyer

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
            yield AccountStatementRow(
                transaction=transaction,
                volume=-transaction.amount_sent
                if user_is_sender
                else transaction.amount_received,
                transaction_type=self._get_transaction_type(
                    transaction=transaction,
                    user_is_sender=user_is_sender,
                    sender=sender,
                    receiver=receiver,
                ),
                account_type=account_type,
                peer=peer,
            )

    def _get_account_owner(self, account_id: UUID) -> AccountOwner:
        result = (
            self.database_gateway.get_accounts()
            .with_id(account_id)
            .joined_with_owner()
            .first()
        )
        assert result
        _, owner = result
        return owner
