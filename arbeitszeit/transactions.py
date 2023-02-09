from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto
from typing import List, Union

from .entities import AccountTypes, Company, Member, SocialAccounting, Transaction
from .repositories import (
    AccountOwnerRepository,
    AccountRepository,
    TransactionRepository,
)


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
class UserAccountingService:
    transaction_repository: TransactionRepository
    account_owner_repository: AccountOwnerRepository
    account_repository: AccountRepository

    def get_all_transactions_sorted(
        self, user: Union[Member, Company]
    ) -> List[Transaction]:
        return list(
            self.transaction_repository.get_transactions()
            .where_account_is_sender_or_receiver(*user.accounts())
            .ordered_by_transaction_date(descending=True)
        )

    def get_account_transactions_sorted(
        self, user: Union[Member, Company], queried_account_type: AccountTypes
    ) -> List[Transaction]:
        accounts = self.account_repository.get_accounts().with_id(*user.accounts())
        for acc in accounts:
            if acc.account_type == queried_account_type:
                queried_account = acc
                break
        else:
            return []
        return list(
            self.transaction_repository.get_transactions()
            .where_account_is_sender_or_receiver(queried_account.id)
            .ordered_by_transaction_date(descending=True)
        )

    def user_is_sender(
        self, transaction: Transaction, user: Union[Member, Company]
    ) -> bool:
        return transaction.sending_account in user.accounts()

    def get_transaction_type(
        self, transaction: Transaction, user_is_sender: bool
    ) -> TransactionTypes:
        """
        Based on wether the user is sender or receiver,
        this method returns the 'subjective' transaction type.
        """
        sender = (
            self.account_repository.get_accounts()
            .with_id(transaction.sending_account)
            .first()
        )
        assert sender
        sending_account = sender.account_type
        receiver = (
            self.account_repository.get_accounts()
            .with_id(transaction.receiving_account)
            .first()
        )
        assert receiver
        receiving_account = receiver.account_type
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
            self.account_repository.get_accounts()
            .with_id(transaction.sending_account)
            .first()
        )
        assert buyer_account
        buyer = self.account_owner_repository.get_account_owner(buyer_account)
        assert not isinstance(
            buyer, SocialAccounting
        )  # from the transactiontype we know: buyer can't be social accounting
        return buyer
