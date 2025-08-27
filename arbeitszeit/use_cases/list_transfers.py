from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, TypeVar
from uuid import UUID

from arbeitszeit.records import AccountOwner
from arbeitszeit.repositories import DatabaseGateway, QueryResult
from arbeitszeit.transfers.transfer_type import TransferType

QueryT = TypeVar("QueryT", bound=QueryResult)


@dataclass
class Request:
    limit: Optional[int]
    offset: Optional[int]


@dataclass
class TransferEntry:
    date: datetime
    debit_account: UUID
    debtor: AccountOwner
    credit_account: UUID
    creditor: AccountOwner
    value: Decimal
    transfer_type: TransferType


@dataclass
class Response:
    request: Request
    total_results: int
    transfers: list[TransferEntry]


@dataclass
class ListTransfersUseCase:
    database_gateway: DatabaseGateway

    def list_transfers(self, request: Request) -> Response:
        transfers = self.database_gateway.get_transfers().ordered_by_date(
            ascending=False
        )
        total_results = len(transfers)
        return Response(
            request=request,
            total_results=total_results,
            transfers=[
                TransferEntry(
                    date=transfer.date,
                    debit_account=transfer.debit_account,
                    debtor=debtor,
                    credit_account=transfer.credit_account,
                    creditor=creditor,
                    value=transfer.value,
                    transfer_type=transfer.type,
                )
                for transfer, debtor, creditor in _limit_results(
                    transfers.joined_with_debtor_and_creditor(),
                    limit=request.limit,
                    offset=request.offset,
                )
            ],
        )


def _limit_results(
    transfers: QueryT, *, limit: Optional[int] = None, offset: Optional[int] = None
) -> QueryT:
    if offset is not None:
        transfers = transfers.offset(n=offset)
    if limit is not None:
        transfers = transfers.limit(n=limit)
    return transfers
