from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers.transfer_type import TransferType


@dataclass
class AccountTransfer:
    type: TransferType
    date: datetime
    volume: Decimal
    is_debit_transfer: bool


@dataclass
class PlotDetails:
    timestamps: list[datetime]
    accumulated_volumes: list[Decimal]


@dataclass
class AccountDetailsService:
    database_gateway: DatabaseGateway

    def get_account_transfers(self, account: UUID) -> list[AccountTransfer]:
        transfers: list[AccountTransfer] = []
        for (
            t
        ) in self.database_gateway.get_transfers().where_account_is_debtor_or_creditor(
            account
        ):
            is_debit_transfer = t.debit_account == account
            transfers.append(
                AccountTransfer(
                    type=t.type,
                    date=t.date,
                    volume=-t.value if is_debit_transfer else t.value,
                    is_debit_transfer=is_debit_transfer,
                )
            )
        return transfers

    def get_account_balance(self, account: UUID) -> Decimal:
        result = (
            self.database_gateway.get_accounts()
            .with_id(account)
            .joined_with_balance()
            .first()
        )
        assert result
        return result[1]


def construct_plot_data(transfers: list[AccountTransfer]) -> PlotDetails:
    transfers = sorted(transfers, key=lambda transfer: transfer.date)
    return PlotDetails(
        timestamps=[t.date for t in transfers],
        accumulated_volumes=list(accumulate([t.volume for t in transfers])),
    )
