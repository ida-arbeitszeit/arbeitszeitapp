from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, TypeVar
from uuid import UUID

from arbeitszeit.records import (
    AccountOwner,
    Company,
    Member,
    SocialAccounting,
)
from arbeitszeit.repositories import DatabaseGateway, QueryResult
from arbeitszeit.transfers.transfer_type import TransferType

QueryT = TypeVar("QueryT", bound=QueryResult)


class AccountOwnerType(Enum):
    member = "member"
    company = "company"
    social_accounting = "social_accounting"
    cooperation = "cooperation"


@dataclass
class Request:
    limit: Optional[int]
    offset: Optional[int]


@dataclass
class TransferEntry:
    date: datetime
    debit_account: UUID | None
    debtor: UUID | None
    debtor_name: str | None
    debtor_type: AccountOwnerType
    credit_account: UUID | None
    creditor: UUID | None
    creditor_name: str | None
    creditor_type: AccountOwnerType
    value: Decimal
    transfer_type: TransferType


@dataclass
class Response:
    total_results: int
    transfers: list[TransferEntry]


@dataclass
class ListTransfersInteractor:
    database_gateway: DatabaseGateway

    def list_transfers(self, request: Request) -> Response:
        transfers = self.database_gateway.get_transfers().ordered_by_date(
            ascending=False
        )
        total_results = len(transfers)
        return Response(
            total_results=total_results,
            transfers=[
                TransferEntry(
                    date=transfer.date,
                    debit_account=(
                        None if isinstance(debtor, Member) else transfer.debit_account
                    ),
                    debtor=None if isinstance(debtor, Member) else debtor.id,
                    debtor_name=self._get_account_owner_name(debtor),
                    debtor_type=self._get_account_owner_type(debtor),
                    credit_account=(
                        None
                        if isinstance(creditor, Member)
                        else transfer.credit_account
                    ),
                    creditor=None if isinstance(creditor, Member) else creditor.id,
                    creditor_name=self._get_account_owner_name(creditor),
                    creditor_type=self._get_account_owner_type(creditor),
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

    def _get_account_owner_name(self, account_owner: AccountOwner) -> str | None:
        if isinstance(account_owner, Member):
            return None
        elif isinstance(account_owner, SocialAccounting):
            return None
        return account_owner.get_name()

    def _get_account_owner_type(self, account_owner: AccountOwner) -> AccountOwnerType:
        if isinstance(account_owner, Company):
            return AccountOwnerType.company
        elif isinstance(account_owner, Member):
            return AccountOwnerType.member
        elif isinstance(account_owner, SocialAccounting):
            return AccountOwnerType.social_accounting
        else:
            return AccountOwnerType.cooperation


def _limit_results(
    transfers: QueryT, *, limit: Optional[int] = None, offset: Optional[int] = None
) -> QueryT:
    if offset is not None:
        transfers = transfers.offset(n=offset)
    if limit is not None:
        transfers = transfers.limit(n=limit)
    return transfers
