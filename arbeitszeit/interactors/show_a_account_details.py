from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from typing import List
from uuid import UUID

from arbeitszeit.records import Company
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers import TransferType


@dataclass
class Request:
    company: UUID


@dataclass
class TransferInfo:
    transfer_type: TransferType
    date: datetime
    transfer_volume: Decimal


@dataclass
class PlotDetails:
    timestamps: List[datetime]
    accumulated_volumes: List[Decimal]


@dataclass
class Response:
    company_id: UUID
    transfers: List[TransferInfo]
    account_balance: Decimal
    plot: PlotDetails


@dataclass
class ShowAAccountDetailsInteractor:
    database: DatabaseGateway

    def show_details(self, request: Request) -> Response:
        company = self.database.get_companies().with_id(request.company).first()
        assert company
        credit_transfers = self._get_credit_transfers(company)
        work_certificates_transfers = self._get_work_certificates_transfers(company)
        transfers: list[TransferInfo] = credit_transfers + work_certificates_transfers
        transfers.sort(key=lambda t: t.date, reverse=True)
        account_balance = self._get_account_balance(company.work_account)
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

    def _get_credit_transfers(self, company: Company) -> list[TransferInfo]:
        credit_transfers_and_debtors = (
            self.database.get_transfers()
            .where_account_is_creditor(company.work_account)
            .joined_with_debtor()
        )
        transfers: list[TransferInfo] = []
        for transfer, debtor in credit_transfers_and_debtors:
            transfers.append(
                TransferInfo(
                    transfer_type=(
                        TransferType.credit_a
                        if isinstance(debtor, Company)
                        else TransferType.credit_public_a
                    ),
                    date=transfer.date,
                    transfer_volume=transfer.value,
                )
            )
        return transfers

    def _get_work_certificates_transfers(self, company: Company) -> list[TransferInfo]:
        transfers_of_work_certificates = (
            self.database.get_transfers().where_account_is_debtor(company.work_account)
        )
        transfers: list[TransferInfo] = []
        for tf in transfers_of_work_certificates:
            transfers.append(
                TransferInfo(
                    transfer_type=TransferType.work_certificates,
                    date=tf.date,
                    transfer_volume=-tf.value,  # negative value because work account is debit account
                )
            )
        return transfers

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
        volumes = [t.transfer_volume for t in transfers]
        volumes.reverse()
        volumes_cumsum = list(accumulate(volumes))
        return volumes_cumsum
