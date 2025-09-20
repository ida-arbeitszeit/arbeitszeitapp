from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers.transfer_type import TransferType


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
    timestamps: list[datetime]
    accumulated_volumes: list[Decimal]


@dataclass
class Response:
    company_id: UUID
    transfers: list[TransferInfo]
    account_balance: Decimal
    plot: PlotDetails


@dataclass
class ShowRAccountDetailsInteractor:
    database: DatabaseGateway

    def show_details(self, request: Request) -> Response:
        company = self.database.get_companies().with_id(request.company).first()
        assert company
        transfers = self._get_transfers_of_account(company.raw_material_account)
        self._invert_sign_of_consumption_transfers(transfers)
        transfers.sort(key=lambda t: t.date, reverse=True)
        account_balance = self._get_account_balance(company.raw_material_account)
        plot = PlotDetails(
            timestamps=self._get_plot_dates(transfers),
            accumulated_volumes=self._get_plot_volumes(transfers),
        )
        return Response(
            company_id=request.company,
            transfers=transfers,
            account_balance=account_balance,
            plot=plot,
        )

    def _get_transfers_of_account(self, account: UUID) -> list[TransferInfo]:
        transfers = [
            TransferInfo(
                type=t.type,
                date=t.date,
                volume=t.value,
            )
            for t in self.database.get_transfers().where_account_is_debtor_or_creditor(
                account
            )
        ]
        return transfers

    def _invert_sign_of_consumption_transfers(
        self, transfers: list[TransferInfo]
    ) -> None:
        for t in transfers:
            if t.type == TransferType.productive_consumption_r:
                t.volume = -t.volume

    def _get_account_balance(self, account: UUID) -> Decimal:
        result = (
            self.database.get_accounts().with_id(account).joined_with_balance().first()
        )
        assert result
        return result[1]

    def _get_plot_dates(self, transfers: list[TransferInfo]) -> list[datetime]:
        timestamps = [t.date for t in transfers]
        timestamps.reverse()
        return timestamps

    def _get_plot_volumes(self, transfers: list[TransferInfo]) -> list[Decimal]:
        volumes = [t.volume for t in transfers]
        volumes.reverse()
        volumes_cumsum = list(accumulate(volumes))
        return volumes_cumsum
