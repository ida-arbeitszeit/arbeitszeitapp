from dataclasses import dataclass
from enum import Enum
from typing import List, Union

from injector import inject

from .entities import AccountTypes, Company, Member, Transaction
from .repositories import TransactionRepository


class CompanyTransactionTypes(Enum):
    credit_for_wages = "Credit for wages"
    payment_of_wages = "Payment of wages"
    credit_for_fixed_means = "Credit for fixed means of production"
    payment_of_fixed_means = "Payment of fixed means of production"
    credit_for_liquid_means = "Credit for liquid means of production"
    payment_of_liquid_means = "Payment of liquid means of production"
    expected_sales = "Debit expected sales"
    sale_of_consumer_product = "Sale of consumer product"
    sale_of_fixed_means = "Sale of fixed means of production"
    sale_of_liquid_means = "Sale of liquid means of production"


transaction_account_dict = {
    CompanyTransactionTypes.credit_for_wages: AccountTypes.a,
    CompanyTransactionTypes.payment_of_wages: AccountTypes.a,
    CompanyTransactionTypes.credit_for_fixed_means: AccountTypes.p,
    CompanyTransactionTypes.payment_of_fixed_means: AccountTypes.p,
    CompanyTransactionTypes.credit_for_liquid_means: AccountTypes.r,
    CompanyTransactionTypes.payment_of_liquid_means: AccountTypes.r,
    CompanyTransactionTypes.sale_of_consumer_product: AccountTypes.prd,
    CompanyTransactionTypes.sale_of_fixed_means: AccountTypes.prd,
    CompanyTransactionTypes.sale_of_liquid_means: AccountTypes.prd,
    CompanyTransactionTypes.expected_sales: AccountTypes.prd,
}


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

    def get_transaction_type(
        self, transaction: Transaction, user_is_sender: bool
    ) -> CompanyTransactionTypes:
        sending_account = transaction.sending_account.account_type.value
        receiving_account = transaction.receiving_account.account_type.value

        if user_is_sender:
            if sending_account == AccountTypes.a.value:
                tt = CompanyTransactionTypes.payment_of_wages
            elif sending_account == AccountTypes.p.value:
                tt = CompanyTransactionTypes.payment_of_fixed_means
            elif sending_account == AccountTypes.r.value:
                tt = CompanyTransactionTypes.payment_of_liquid_means

        else:
            if sending_account == AccountTypes.accounting.value:
                if receiving_account == AccountTypes.a.value:
                    tt = CompanyTransactionTypes.credit_for_wages
                elif receiving_account == AccountTypes.p.value:
                    tt = CompanyTransactionTypes.credit_for_fixed_means
                elif receiving_account == AccountTypes.r.value:
                    tt = CompanyTransactionTypes.credit_for_liquid_means
                elif receiving_account == AccountTypes.prd.value:
                    tt = CompanyTransactionTypes.expected_sales

            elif sending_account == AccountTypes.p.value:
                tt = CompanyTransactionTypes.sale_of_fixed_means
            elif sending_account == AccountTypes.r.value:
                tt = CompanyTransactionTypes.sale_of_liquid_means
            elif sending_account == AccountTypes.member.value:
                tt = CompanyTransactionTypes.sale_of_consumer_product

        assert tt
        return tt
