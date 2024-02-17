from dataclasses import dataclass
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import AccountTypes
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.get_company_transactions import (
    GetCompanyTransactionsResponse,
    TransactionInfo,
)
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem


@dataclass
class ViewModelTransactionInfo:
    transaction_type: str
    date: str
    transaction_volume: Decimal
    account: str
    purpose: str


@dataclass
class GetCompanyTransactionsViewModel:
    transactions: List[ViewModelTransactionInfo]
    navbar_items: list[NavbarItem]


@dataclass
class GetCompanyTransactionsPresenter:
    translator: Translator
    datetime_service: DatetimeService
    url_index: UrlIndex

    def present(
        self, use_case_response: GetCompanyTransactionsResponse
    ) -> GetCompanyTransactionsViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transactions
        ]
        return GetCompanyTransactionsViewModel(
            transactions=transactions,
            navbar_items=self._create_navbar_items(
                company_id=use_case_response.company_id
            ),
        )

    def _create_info(self, transaction: TransactionInfo) -> ViewModelTransactionInfo:
        account = self._get_account(transaction.account_type)
        return ViewModelTransactionInfo(
            transaction_type=self._get_transaction_name(transaction.transaction_type),
            date=self.datetime_service.format_datetime(
                transaction.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
            transaction_volume=round(transaction.transaction_volume, 2),
            account=account,
            purpose=transaction.purpose,
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
            consumption_of_fixed_means=self.translator.gettext(
                "Consumption of fixed means of production"
            ),
            credit_for_liquid_means=self.translator.gettext(
                "Credit for liquid means of production"
            ),
            consumption_of_liquid_means=self.translator.gettext(
                "Consumption of liquid means of production"
            ),
            expected_sales=self.translator.gettext("Debit expected sales"),
            sale_of_consumer_product=self.translator.gettext(
                "Sale of consumer product"
            ),
            private_consumption=self.translator.gettext("Private consumption"),
            sale_of_fixed_means=self.translator.gettext(
                "Sale of fixed means of production"
            ),
            sale_of_liquid_means=self.translator.gettext(
                "Sale of liquid means of production"
            ),
        )
        return transaction_dict[transaction_type.name]

    def _create_navbar_items(self, company_id: UUID) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("Accounts"),
                url=self.url_index.get_company_accounts_url(company_id=company_id),
            ),
            NavbarItem(
                text=self.translator.gettext("All transactions"),
                url=None,
            ),
        ]
