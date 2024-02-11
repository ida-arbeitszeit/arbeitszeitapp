from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from typing import List
from uuid import UUID

from arbeitszeit.records import AccountOwner, Company, Member
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transactions import TransactionTypes, UserAccountingService


@dataclass
class ShowPRDAccountDetailsUseCase:
    class MemberPeer:
        ...

    @dataclass
    class CompanyPeer:
        name: str
        id: UUID

    @dataclass
    class SocialAccountingPeer:
        id: UUID

    @dataclass
    class TransactionInfo:
        transaction_type: TransactionTypes
        date: datetime
        transaction_volume: Decimal
        purpose: str
        peer: (
            ShowPRDAccountDetailsUseCase.MemberPeer
            | ShowPRDAccountDetailsUseCase.SocialAccountingPeer
            | ShowPRDAccountDetailsUseCase.CompanyPeer
        )

    @dataclass
    class PlotDetails:
        timestamps: List[datetime]
        accumulated_volumes: List[Decimal]

    @dataclass
    class Response:
        company_id: UUID
        transactions: List[ShowPRDAccountDetailsUseCase.TransactionInfo]
        account_balance: Decimal
        plot: ShowPRDAccountDetailsUseCase.PlotDetails

    accounting_service: UserAccountingService
    database: DatabaseGateway

    def __call__(self, company_id: UUID) -> Response:
        company = self.database.get_companies().with_id(company_id).first()
        assert company
        transactions = [
            self.TransactionInfo(
                transaction_type=row.transaction_type,
                date=row.transaction.date,
                transaction_volume=row.volume,
                purpose=row.transaction.purpose,
                peer=self._create_peer_info(row.peer),
            )
            for row in self.accounting_service.get_statement_of_account(
                company, [company.product_account]
            )
        ]
        transactions_ascending = transactions.copy()
        transactions_ascending.reverse()
        account_balance = self._get_account_balance(company.product_account)
        plot = self.PlotDetails(
            timestamps=self._get_plot_dates(transactions_ascending),
            accumulated_volumes=self._get_plot_volumes(transactions_ascending),
        )
        return self.Response(
            company_id=company_id,
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
        return timestamps

    def _get_plot_volumes(self, transactions: List[TransactionInfo]) -> List[Decimal]:
        volumes_cumsum = list(accumulate(t.transaction_volume for t in transactions))
        return volumes_cumsum

    def _create_peer_info(
        self, peer: AccountOwner
    ) -> (
        ShowPRDAccountDetailsUseCase.MemberPeer
        | ShowPRDAccountDetailsUseCase.SocialAccountingPeer
        | ShowPRDAccountDetailsUseCase.CompanyPeer
    ):
        if isinstance(peer, Member):
            return self.MemberPeer()
        elif isinstance(peer, Company):
            return self.CompanyPeer(
                id=peer.id,
                name=peer.get_name(),
            )
        else:
            return self.SocialAccountingPeer(id=peer.id)
