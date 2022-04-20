from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import AccountTypes, Company, Transaction
from arbeitszeit.repositories import AccountRepository, CompanyRepository
from arbeitszeit.transactions import TransactionTypes, UserAccountingService


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
class ShowPRDAccountDetailsResponse:
    transactions: List[TransactionInfo]
    account_balance: Decimal
    plot: PlotDetails


@inject
@dataclass
class ShowPRDAccountDetails:
    accounting_service: UserAccountingService
    company_repository: CompanyRepository
    account_repository: AccountRepository

    def __call__(self, company_id: UUID) -> ShowPRDAccountDetailsResponse:
        company = self.company_repository.get_by_id(company_id)
        assert company
        transactions = [
            self._create_info(company, transaction)
            for transaction in self.accounting_service.get_account_transactions_sorted(
                company, AccountTypes.prd
            )
        ]
        account_balance = self.account_repository.get_account_balance(
            company.product_account
        )
        plot = PlotDetails(
            timestamps=self._get_plot_dates(transactions),
            accumulated_volumes=self._get_plot_volumes(transactions),
        )
        return ShowPRDAccountDetailsResponse(
            transactions=transactions, account_balance=account_balance, plot=plot
        )

    def _create_info(
        self,
        company: Company,
        transaction: Transaction,
    ) -> TransactionInfo:
        user_is_sender = self.accounting_service.user_is_sender(transaction, company)
        transaction_type = self.accounting_service.get_transaction_type(
            transaction, user_is_sender
        )
        transaction_volume = self.accounting_service.get_transaction_volume(
            transaction,
            user_is_sender,
        )
        return TransactionInfo(
            transaction_type,
            transaction.date,
            transaction_volume,
            transaction.purpose,
        )

    def _get_plot_dates(self, transactions: List[TransactionInfo]) -> List[datetime]:
        timestamps = [t.date for t in transactions]
        timestamps.reverse()
        return timestamps

    def _get_plot_volumes(self, transactions: List[TransactionInfo]) -> List[Decimal]:
        volumes = [t.transaction_volume for t in transactions]
        volumes.reverse()
        volumes_cumsum = self._cumsum(volumes)
        return volumes_cumsum

    def _cumsum(self, trans_volumes: List[Decimal]) -> List[Decimal]:
        cum_list = []
        y = Decimal("0")
        for x in range(len(trans_volumes)):
            y += trans_volumes[x]
            cum_list.append(y)
        return cum_list
