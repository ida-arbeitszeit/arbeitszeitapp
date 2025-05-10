from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from typing import List
from uuid import UUID

from arbeitszeit.records import Company
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers.transfer_type import TransferType


@dataclass
class ShowPAccountDetailsUseCase:
    @dataclass
    class Request:
        company: UUID

    @dataclass
    class TransferInfo:
        type: TransferType
        date: datetime
        volume: Decimal

    @dataclass
    class PlotDetails:
        timestamps: List[datetime]
        accumulated_volumes: List[Decimal]

    @dataclass
    class Response:
        company_id: UUID
        transfers: List[ShowPAccountDetailsUseCase.TransferInfo]
        account_balance: Decimal
        plot: ShowPAccountDetailsUseCase.PlotDetails

    database: DatabaseGateway

    def show_details(self, request: Request) -> Response:
        company = self.database.get_companies().with_id(request.company).first()
        assert company
        transfers: list[ShowPAccountDetailsUseCase.TransferInfo] = []
        self._add_credit_transfers(company, transfers)
        self._add_consumption_transfers(company, transfers)
        transfers.sort(key=lambda t: t.date, reverse=True)
        account_balance = self._get_account_balance(company.means_account)
        plot = self.PlotDetails(
            timestamps=self._get_plot_dates(transfers),
            accumulated_volumes=self._get_plot_volumes(transfers),
        )
        return self.Response(
            company_id=request.company,
            transfers=transfers,
            account_balance=account_balance,
            plot=plot,
        )

    def _add_credit_transfers(
        self, company: Company, transfers: list[TransferInfo]
    ) -> None:
        credit_transfers_and_debtors = (
            self.database.get_transfers()
            .where_account_is_creditor(company.means_account)
            .joined_with_debtor()
        )
        for transfer, debtor in credit_transfers_and_debtors:
            transfers.append(
                self.TransferInfo(
                    type=(
                        TransferType.credit_p
                        if isinstance(debtor, Company)
                        else TransferType.credit_public_p
                    ),
                    date=transfer.date,
                    volume=transfer.value,
                )
            )

    def _add_consumption_transfers(
        self, company: Company, transfers: list[TransferInfo]
    ) -> None:
        transactions = self.database.get_transactions().where_account_is_sender(
            company.means_account
        )
        for transaction in transactions:
            transfers.append(
                self.TransferInfo(
                    type=TransferType.productive_consumption_p,
                    date=transaction.date,
                    volume=-transaction.amount_sent,
                )
            )

    def _get_account_balance(self, account: UUID) -> Decimal:
        result = (
            self.database.get_accounts().with_id(account).joined_with_balance().first()
        )
        assert result
        return result[1]

    def _get_plot_dates(self, transfers: List[TransferInfo]) -> List[datetime]:
        timestamps = [t.date for t in transfers]
        timestamps.reverse()
        return timestamps

    def _get_plot_volumes(self, transfers: List[TransferInfo]) -> List[Decimal]:
        volumes = [t.volume for t in transfers]
        volumes.reverse()
        volumes_cumsum = list(accumulate(volumes))
        return volumes_cumsum
