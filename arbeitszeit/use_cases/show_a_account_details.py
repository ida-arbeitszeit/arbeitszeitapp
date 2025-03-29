from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from typing import List
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers import TransferType


@dataclass
class Request:
    company: UUID


@dataclass
class TransactionInfo:
    transaction_type: TransferType
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
    transactions: List[TransactionInfo]
    account_balance: Decimal
    plot: PlotDetails


@dataclass
class ShowAAccountDetailsUseCase:
    database: DatabaseGateway

    def show_details(self, request: Request) -> Response:
        company = self.database.get_companies().with_id(request.company).first()
        assert company
        transactions: list[TransactionInfo] = []
        transactions_of_credit_a = (
            self.database.get_transactions().where_account_is_receiver(
                company.work_account
            )
        )
        transfers_of_work_certificates = (
            self.database.get_transfers().where_account_is_debtor(company.work_account)
        )
        for tx in transactions_of_credit_a:
            transactions.append(
                TransactionInfo(
                    transaction_type=TransferType.credit_a,  # in the new "transfer" system this can be also credit_public_a
                    date=tx.date,
                    transaction_volume=tx.amount_received,
                    purpose=tx.purpose,
                )
            )
        for tf in transfers_of_work_certificates:
            transactions.append(
                TransactionInfo(
                    transaction_type=TransferType.work_certificates,
                    date=tf.date,
                    transaction_volume=-tf.value,  # negative value
                    purpose="Lohn",
                )
            )
        transactions.sort(key=lambda t: t.date, reverse=True)
        account_balance = self._get_account_balance(company.work_account)
        plot = PlotDetails(
            timestamps=self._get_plot_dates(transactions),
            accumulated_volumes=self._get_plot_volumes(transactions),
        )
        return Response(
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
