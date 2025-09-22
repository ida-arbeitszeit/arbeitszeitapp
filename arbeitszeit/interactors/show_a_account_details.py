from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.account_details import (
    AccountDetailsService,
    AccountTransfer,
    PlotDetails,
    construct_plot_data,
)
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    company: UUID


@dataclass
class Response:
    company_id: UUID
    transfers: list[AccountTransfer]
    account_balance: Decimal
    plot: PlotDetails


@dataclass
class ShowAAccountDetailsInteractor:
    database: DatabaseGateway
    account_details_service: AccountDetailsService

    def show_details(self, request: Request) -> Response:
        company = self.database.get_companies().with_id(request.company).first()
        assert company
        account = company.work_account
        transfers = self.account_details_service.get_account_transfers(account)
        account_balance = self.account_details_service.get_account_balance(account)
        return Response(
            company_id=request.company,
            transfers=sorted(transfers, key=lambda t: t.date, reverse=True),
            account_balance=account_balance,
            plot=construct_plot_data(transfers),
        )
