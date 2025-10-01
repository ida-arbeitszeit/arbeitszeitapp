from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.services.account_details import (
    AccountDetailsService,
    AccountTransfer,
    PlotDetails,
    construct_plot_data,
)


@dataclass
class Request:
    company_id: UUID


@dataclass
class Response:
    company_id: UUID
    transfers: list[AccountTransfer]
    account_balance: Decimal
    plot: PlotDetails


@dataclass
class ShowPRDAccountDetailsInteractor:
    database_gateway: DatabaseGateway
    account_details_service: AccountDetailsService

    def show_details(self, request: Request) -> Response:
        company = (
            self.database_gateway.get_companies().with_id(request.company_id).first()
        )
        assert company
        account = company.product_account
        transfers = self.account_details_service.get_account_transfers(account)
        account_balance = self.account_details_service.get_account_balance(account)
        return Response(
            company_id=request.company_id,
            transfers=sorted(transfers, key=lambda t: t.date, reverse=True),
            account_balance=account_balance,
            plot=construct_plot_data(transfers),
        )
