from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from uuid import UUID

from arbeitszeit.records import (
    AccountOwner,
    AccountTypes,
    Company,
    Cooperation,
    Member,
    Transaction,
)
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers.transfer_type import TransferType


@dataclass
class Request:
    company_id: UUID


class MemberPeer: ...


@dataclass
class CompanyPeer:
    name: str
    id: UUID


@dataclass
class CooperationPeer:
    name: str
    id: UUID


@dataclass
class TransferInfo:
    type: TransferType
    date: datetime
    volume: Decimal
    peer: MemberPeer | CompanyPeer | CooperationPeer | None


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
class ShowPRDAccountDetailsUseCase:
    database: DatabaseGateway

    def show_details(self, request: Request) -> Response:
        company = self.database.get_companies().with_id(request.company_id).first()
        assert company
        credit_and_compensation_transfers = (
            self._get_credit_and_compensation_for_coop_transfers(company)
        )
        private_consumption_and_compensation_for_company_transfers = (
            self._get_private_consumption_and_compensation_for_company_transfers(
                company
            )
        )
        productive_consumption_transfers = self._get_productive_consumption_transfers(
            company
        )
        transfers = (
            credit_and_compensation_transfers
            + productive_consumption_transfers
            + private_consumption_and_compensation_for_company_transfers
        )
        transfers.sort(key=lambda t: t.date)
        transfers_descending = transfers.copy()
        transfers_descending.reverse()
        account_balance = self._get_account_balance(company.product_account)
        plot = PlotDetails(
            timestamps=self._get_plot_dates_in_ascending_order(transfers),
            accumulated_volumes=self._get_accumulated_plot_volumes_in_ascending_order(
                transfers
            ),
        )
        return Response(
            company_id=request.company_id,
            transfers=transfers_descending,
            account_balance=account_balance,
            plot=plot,
        )

    def _get_credit_and_compensation_for_coop_transfers(
        self, company: Company
    ) -> list[TransferInfo]:
        debit_transfers_and_creditor = (
            self.database.get_transfers()
            .where_account_is_debtor(company.product_account)
            .joined_with_creditor()
        )
        transfers: list[TransferInfo] = []
        for transfer, creditor in debit_transfers_and_creditor:
            if transfer.type in [
                TransferType.credit_p,
                TransferType.credit_r,
                TransferType.credit_a,
            ]:
                transfers.append(
                    TransferInfo(
                        type=transfer.type,
                        date=transfer.date,
                        volume=-transfer.value,  # negative because account is debit account
                        peer=None,
                    )
                )
            elif transfer.type == TransferType.compensation_for_coop:
                transfers.append(
                    TransferInfo(
                        type=TransferType.compensation_for_coop,
                        date=transfer.date,
                        volume=-transfer.value,  # negative because account is debit account
                        peer=self._create_peer_info(creditor),
                    )
                )
        return transfers

    def _get_private_consumption_and_compensation_for_company_transfers(
        self, company: Company
    ) -> list[TransferInfo]:
        transfers_and_debtor = (
            self.database.get_transfers()
            .where_account_is_creditor(company.product_account)
            .joined_with_debtor()
        )
        transfers: list[TransferInfo] = []
        for transfer, debtor in transfers_and_debtor:
            transfers.append(
                TransferInfo(
                    type=transfer.type,
                    date=transfer.date,
                    volume=transfer.value,
                    peer=self._create_peer_info(debtor),
                )
            )
        return transfers

    def _get_productive_consumption_transfers(
        self, company: Company
    ) -> list[TransferInfo]:
        transactions_and_sender_and_receiver = (
            self.database.get_transactions()
            .where_account_is_receiver(company.product_account)
            .joined_with_sender_and_receiver()
        )
        transfers: list[TransferInfo] = []
        for transaction, sender, _ in transactions_and_sender_and_receiver:
            transfers.append(
                TransferInfo(
                    type=self._determine_sale_type(sender, transaction),
                    date=transaction.date,
                    volume=transaction.amount_received,
                    peer=self._create_peer_info(sender),
                )
            )
        return transfers

    def _determine_sale_type(
        self, account_owner: AccountOwner, transaction: Transaction
    ) -> TransferType:
        if isinstance(account_owner, Member):
            return TransferType.private_consumption
        else:
            sending_account_type = account_owner.get_account_type(
                transaction.sending_account
            )
            if sending_account_type == AccountTypes.p:
                return TransferType.productive_consumption_p
            else:
                return TransferType.productive_consumption_r

    def _get_account_balance(self, account: UUID) -> Decimal:
        result = (
            self.database.get_accounts().with_id(account).joined_with_balance().first()
        )
        assert result
        return result[1]

    def _get_plot_dates_in_ascending_order(
        self, transfers: list[TransferInfo]
    ) -> list[datetime]:
        timestamps = [t.date for t in transfers]
        return timestamps

    def _get_accumulated_plot_volumes_in_ascending_order(
        self, transfers: list[TransferInfo]
    ) -> list[Decimal]:
        volumes_cumsum = list(accumulate(t.volume for t in transfers))
        return volumes_cumsum

    def _create_peer_info(
        self, peer: AccountOwner
    ) -> MemberPeer | CompanyPeer | CooperationPeer:
        if isinstance(peer, Member):
            return MemberPeer()
        elif isinstance(peer, Cooperation):
            return CooperationPeer(
                id=peer.id,
                name=peer.get_name(),
            )
        return CompanyPeer(
            id=peer.id,
            name=peer.get_name(),
        )
