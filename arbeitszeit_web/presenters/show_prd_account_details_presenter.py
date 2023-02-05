from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_prd_account_details import ShowPRDAccountDetailsUseCase
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ShowPRDAccountDetailsPresenter:
    @dataclass
    class TransactionInfo:
        transaction_type: str
        date: str
        transaction_volume: str
        purpose: str
        buyer_name: str
        buyer_type_icon: Optional[str]

    @dataclass
    class ViewModel:
        transactions: List[ShowPRDAccountDetailsPresenter.TransactionInfo]
        show_transactions: bool
        account_balance: str
        plot_url: str

    translator: Translator
    url_index: UrlIndex
    datetime_service: DatetimeService

    def present(
        self, use_case_response: ShowPRDAccountDetailsUseCase.Response
    ) -> ViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transactions
        ]
        return self.ViewModel(
            transactions=transactions,
            show_transactions=bool(transactions),
            account_balance=str(round(use_case_response.account_balance, 2)),
            plot_url=self.url_index.get_line_plot_of_company_prd_account(
                use_case_response.company_id
            ),
        )

    def _create_info(
        self, transaction: ShowPRDAccountDetailsUseCase.TransactionInfo
    ) -> TransactionInfo:
        assert transaction.transaction_type in [
            TransactionTypes.sale_of_consumer_product,
            TransactionTypes.sale_of_fixed_means,
            TransactionTypes.sale_of_liquid_means,
            TransactionTypes.expected_sales,
        ]
        transaction_type = (
            self.translator.gettext("Debit expected sales")
            if transaction.transaction_type == TransactionTypes.expected_sales
            else self.translator.gettext("Sale")
        )
        return self.TransactionInfo(
            transaction_type=transaction_type,
            date=self.datetime_service.format_datetime(
                date=transaction.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
            transaction_volume=str(round(transaction.transaction_volume, 2)),
            purpose=transaction.purpose,
            buyer_name=transaction.buyer.buyer_name if transaction.buyer else "",
            buyer_type_icon=self._get_buyer_type_icon(transaction.buyer),
        )

    def _get_buyer_type_icon(
        self, buyer: Optional[ShowPRDAccountDetailsUseCase.Buyer]
    ) -> Optional[str]:
        if not buyer:
            return None
        elif buyer.buyer_is_member:
            return "fas fa-user"
        else:
            return "fas fa-industry"
