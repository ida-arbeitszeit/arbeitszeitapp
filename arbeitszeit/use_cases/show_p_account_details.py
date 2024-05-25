from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from typing import List
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transactions import TransactionTypes, UserAccountingService


@dataclass
class ShowPAccountDetailsUseCase:
    @dataclass
    class Request:
        company: UUID

    @dataclass
    class TransactionInfo:
        transaction_type: TransactionTypes
        date: datetime
        transaction_volume: Decimal
        purpose: str

    @dataclass
    class PlotDetails:
        timestamps: List[datetime]
        accumulated_volumes: List[Decimal]

    @dataclass
    class Response:
        company_id: UUID
        transactions: List[ShowPAccountDetailsUseCase.TransactionInfo]
        account_balance: Decimal
        plot: ShowPAccountDetailsUseCase.PlotDetails

    accounting_service: UserAccountingService
    database: DatabaseGateway

    def show_details(self, request: Request) -> Response:
        company = self.database.get_companies().with_id(request.company).first()
        assert company
        transactions = [
            self.TransactionInfo(
                transaction_type=row.transaction_type,
                date=row.transaction.date,
                transaction_volume=row.volume,
                purpose=row.transaction.purpose,
            )
            for row in self.accounting_service.get_statement_of_account(
                company, [company.means_account]
            )
        ]
        account_balance = self._get_account_balance(company.means_account)
        plot = self.PlotDetails(
            timestamps=self._get_plot_dates(transactions),
            accumulated_volumes=self._get_plot_volumes(transactions),
        )
        return self.Response(
            company_id=request.company,
            transactions=transactions,
            account_balance=account_balance,
            plot=plot,
        )

    def _get_account_balance(self, account: UUID) -> Decimal:
        result = (
            self.database.get_accounts().with_id(account).joined_with_balance().first()
        )
        assert result
        return result[1]

    def _get_plot_dates(self, transactions: List[TransactionInfo]) -> List[datetime]:
        timestamps = [t.date for t in transactions]
        timestamps.reverse()
        return timestamps

    def _get_plot_volumes(self, transactions: List[TransactionInfo]) -> List[Decimal]:
        volumes = [t.transaction_volume for t in transactions]
        volumes.reverse()
        volumes_cumsum = list(accumulate(volumes))
        return volumes_cumsum
