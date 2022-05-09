from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from arbeitszeit.entities import AccountTypes
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.get_company_transactions import (
    GetCompanyTransactionsResponse,
    TransactionInfo,
)
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModelTransactionInfo:
    transaction_type: str
    date: datetime
    transaction_volume: Decimal
    account: str
    purpose: str


@dataclass
class GetCompanyTransactionsViewModel:
    transactions: List[ViewModelTransactionInfo]


@dataclass
class GetCompanyTransactionsPresenter:
    translator: Translator

    def present(
        self, use_case_response: GetCompanyTransactionsResponse
    ) -> GetCompanyTransactionsViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transactions
        ]

        return GetCompanyTransactionsViewModel(transactions=transactions)

    def _create_info(self, transaction: TransactionInfo) -> ViewModelTransactionInfo:
        account = self._get_account(transaction.account_type)
        return ViewModelTransactionInfo(
            self._get_transaction_name(transaction.transaction_type),
            transaction.date,
            round(transaction.transaction_volume, 2),
            account,
            transaction.purpose,
        )

    def _get_account(self, account_type: AccountTypes) -> str:
        type_to_string_dict = {
            AccountTypes.p: self.translator.gettext("Account p"),
            AccountTypes.r: self.translator.gettext("Account r"),
            AccountTypes.a: self.translator.gettext("Account a"),
            AccountTypes.prd: self.translator.gettext("Account prd"),
        }
        return type_to_string_dict[account_type]

    def _get_transaction_name(self, transaction_type: TransactionTypes) -> str:
        transaction_dict = dict(
            credit_for_wages=self.translator.gettext("Credit for wages"),
            payment_of_wages=self.translator.gettext("Payment of wages"),
            incoming_wages=self.translator.gettext("Incoming wages"),
            credit_for_fixed_means=self.translator.gettext(
                "Credit for fixed means of production"
            ),
            payment_of_fixed_means=self.translator.gettext(
                "Payment of fixed means of production"
            ),
            credit_for_liquid_means=self.translator.gettext(
                "Credit for liquid means of production"
            ),
            payment_of_liquid_means=self.translator.gettext(
                "Payment of liquid means of production"
            ),
            expected_sales=self.translator.gettext("Debit expected sales"),
            sale_of_consumer_product=self.translator.gettext(
                "Sale of consumer product"
            ),
            payment_of_consumer_product=self.translator.gettext(
                "Payment of consumer product"
            ),
            sale_of_fixed_means=self.translator.gettext(
                "Sale of fixed means of production"
            ),
            sale_of_liquid_means=self.translator.gettext(
                "Sale of liquid means of production"
            ),
        )
        return transaction_dict[transaction_type.name]
