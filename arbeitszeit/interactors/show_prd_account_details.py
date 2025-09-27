from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from uuid import UUID

from arbeitszeit.records import AccountOwner, Cooperation, Member
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers import TransferType


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
class ShowPRDAccountDetailsInteractor:
    database_gateway: DatabaseGateway

    def show_details(self, request: Request) -> Response:
        company = (
            self.database_gateway.get_companies().with_id(request.company_id).first()
        )
        assert company
        transfers = self._get_account_transfers(company.product_account)
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

    def _get_account_transfers(self, account: UUID) -> list[TransferInfo]:
        transfers: list[TransferInfo] = []
        for transfer, debtor, creditor in (
            self.database_gateway.get_transfers()
            .where_account_is_debtor_or_creditor(account)
            .joined_with_debtor_and_creditor()
        ):
            is_debit_transfer = transfer.debit_account == account
            transfers.append(
                TransferInfo(
                    type=transfer.type,
                    date=transfer.date,
                    volume=-transfer.value if is_debit_transfer else transfer.value,
                    peer=self._create_peer_info(
                        debtor, creditor, is_debit_transfer, transfer.type
                    ),
                )
            )
        return transfers

    def _get_account_balance(self, account: UUID) -> Decimal:
        result = (
            self.database_gateway.get_accounts()
            .with_id(account)
            .joined_with_balance()
            .first()
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
        self,
        debtor: AccountOwner,
        creditor: AccountOwner,
        is_debit_transfer: bool,
        transfer_type: TransferType,
    ) -> MemberPeer | CompanyPeer | CooperationPeer | None:
        if transfer_type in [
            TransferType.credit_p,
            TransferType.credit_r,
            TransferType.credit_a,
        ]:
            #  Transfer comes from one of company's own accounts
            return None
        peer = creditor if is_debit_transfer else debtor
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
