from dataclasses import dataclass
from enum import Enum
from typing import List, Union

from injector import inject

from .entities import AccountTypes, Company, Member, Transaction
from .repositories import TransactionRepository


class TransactionTypes(Enum):
    credit_for_wages = "Credit for wages"
    payment_of_wages = "Payment of wages"
    incoming_wages = "Incoming wages"
    credit_for_fixed_means = "Credit for fixed means of production"
    payment_of_fixed_means = "Payment of fixed means of production"
    credit_for_liquid_means = "Credit for liquid means of production"
    payment_of_liquid_means = "Payment of liquid means of production"
    expected_sales = "Debit expected sales"
    sale_of_consumer_product = "Sale of consumer product"
    payment_of_consumer_product = "Payment of consumer product"
    sale_of_fixed_means = "Sale of fixed means of production"
    sale_of_liquid_means = "Sale of liquid means of production"


@inject
@dataclass
class UserAccountingService:
    transaction_repository: TransactionRepository

    def get_all_transactions_sorted(
        self, user: Union[Member, Company]
    ) -> List[Transaction]:
        all_transactions = set()
        for account in user.accounts():
            all_transactions.update(
                self.transaction_repository.all_transactions_sent_by_account(account)
            )
            all_transactions.update(
                self.transaction_repository.all_transactions_received_by_account(
                    account
                )
            )
        all_transactions_sorted = sorted(
            all_transactions, key=lambda x: x.date, reverse=True
        )
        return all_transactions_sorted

    def get_account_p_transactions_sorted(self, company: Company) -> List[Transaction]:
        account_p = company.means_account
        transactions = set()
        transactions.update(
            self.transaction_repository.all_transactions_sent_by_account(account_p)
        )
        transactions.update(
            self.transaction_repository.all_transactions_received_by_account(account_p)
        )
        transactions_sorted = sorted(transactions, key=lambda x: x.date, reverse=True)
        return transactions_sorted

    def get_transaction_type(
        self, transaction: Transaction, user_is_sender: bool
    ) -> TransactionTypes:
        """
        Based on wether the user is sender or receiver of a transaction,
        this method returns the transaction type.
        """
        sending_account = transaction.sending_account.account_type
        receiving_account = transaction.receiving_account.account_type

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
            elif sending_account == AccountTypes.member:
                transaction_type = TransactionTypes.sale_of_consumer_product

        assert transaction_type
        return transaction_type
