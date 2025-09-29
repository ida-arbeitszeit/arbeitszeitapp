from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from arbeitszeit.interactors.list_transfers import AccountOwnerType
from arbeitszeit.interactors.list_transfers import Response as InteractorResponse
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.pagination import Pagination, Paginator
from arbeitszeit_web.request import Request
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.presenters.transfers import (
    transfer_description_from_transfer_type,
)


@dataclass
class ResultTableRow:
    date: str
    transfer_type: str
    debit_account: str
    debtor_name: str
    debtor_url: str | None
    credit_account: str
    creditor_name: str
    creditor_url: str | None
    value: str


@dataclass
class ResultsTable:
    rows: list[ResultTableRow]


@dataclass
class ListTransfersViewModel:
    pagination: Pagination
    results: ResultsTable
    show_results: bool
    total_results: int


@dataclass
class ListTransfersPresenter:
    web_request: Request
    translator: Translator
    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter

    def present(self, response: InteractorResponse) -> ListTransfersViewModel:
        pagination = self._create_pagination(response)
        return ListTransfersViewModel(
            pagination=pagination,
            results=self._create_results_table(response),
            show_results=bool(response.transfers),
            total_results=response.total_results,
        )

    def _create_results_table(self, response: InteractorResponse) -> ResultsTable:
        rows = [
            ResultTableRow(
                date=self._format_date(transfer.date),
                transfer_type=transfer_description_from_transfer_type(
                    self.translator, transfer.transfer_type
                ),
                debit_account=(
                    str(transfer.debit_account) if transfer.debit_account else ""
                ),
                debtor_name=self._convert_account_owner_name(
                    transfer.debtor_name, transfer.debtor_type
                ),
                debtor_url=self._get_account_owner_url(
                    transfer.debtor, transfer.debtor_type
                ),
                credit_account=(
                    str(transfer.credit_account) if transfer.credit_account else ""
                ),
                creditor_name=self._convert_account_owner_name(
                    transfer.creditor_name, transfer.creditor_type
                ),
                creditor_url=self._get_account_owner_url(
                    transfer.creditor, transfer.creditor_type
                ),
                value=self._format_value(transfer.value),
            )
            for transfer in response.transfers
        ]
        return ResultsTable(rows=rows)

    def _create_pagination(self, response: InteractorResponse) -> Pagination:
        paginator = Paginator(
            request=self.web_request,
            total_results=response.total_results,
        )
        pagination = Pagination(
            is_visible=paginator.number_of_pages > 1,
            pages=paginator.get_pages(),
        )
        return pagination

    def _format_date(self, date: datetime) -> str:
        return self.datetime_formatter.format_datetime(
            date,
            fmt="%d.%m.%Y %H:%M",
        )

    def _convert_account_owner_name(
        self, name: str | None, owner_type: AccountOwnerType
    ) -> str:
        if owner_type == AccountOwnerType.member:
            return self.translator.gettext("Member")  # anonymized
        elif owner_type == AccountOwnerType.company:
            assert name is not None
            return name
        elif owner_type == AccountOwnerType.social_accounting:
            return self.translator.gettext("Social Accounting")
        elif owner_type == AccountOwnerType.cooperation:
            assert name is not None
            return name

    def _get_account_owner_url(
        self, account_owner: UUID | None, owner_type: AccountOwnerType
    ) -> str | None:
        if owner_type == AccountOwnerType.company:
            assert account_owner is not None
            return self.url_index.get_company_summary_url(company_id=account_owner)
        elif owner_type == AccountOwnerType.cooperation:
            assert account_owner is not None
            return self.url_index.get_coop_summary_url(coop_id=account_owner)
        return None

    def _format_value(self, value: Decimal) -> str:
        return f"{value:.2f}"
