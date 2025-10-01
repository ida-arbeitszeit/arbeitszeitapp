import enum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import accumulate
from uuid import UUID

from arbeitszeit.anonymization import (
    ANONYMIZED_STR,
    ANONYMIZED_UUID,
    MaybeAnonymizedStr,
    MaybeAnonymizedUUID,
)
from arbeitszeit.records import (
    AccountOwner,
    Company,
    Cooperation,
    Member,
    SocialAccounting,
)
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transfers import TransferType


class TransferPartyType(enum.Enum):
    member = enum.auto()
    company = enum.auto()
    social_accounting = enum.auto()
    cooperation = enum.auto()


@dataclass
class TransferParty:
    type: TransferPartyType
    id: MaybeAnonymizedUUID
    name: MaybeAnonymizedStr


@dataclass
class AccountTransfer:
    type: TransferType
    date: datetime
    volume: Decimal
    is_debit_transfer: bool
    transfer_party: TransferParty
    debtor_equals_creditor: bool


@dataclass
class PlotDetails:
    timestamps: list[datetime]
    accumulated_volumes: list[Decimal]


@dataclass
class AccountDetailsService:
    database_gateway: DatabaseGateway

    def get_account_transfers(self, account: UUID) -> list[AccountTransfer]:
        transfers: list[AccountTransfer] = []
        for transfer, debtor, creditor in (
            self.database_gateway.get_transfers()
            .where_account_is_debtor_or_creditor(account)
            .joined_with_debtor_and_creditor()
        ):
            is_debit_transfer = transfer.debit_account == account
            transfer_party = build_counterparty_transfer_party(
                debtor=debtor,
                creditor=creditor,
                is_debit_transfer=is_debit_transfer,
            )
            transfers.append(
                AccountTransfer(
                    type=transfer.type,
                    date=transfer.date,
                    volume=-transfer.value if is_debit_transfer else transfer.value,
                    is_debit_transfer=is_debit_transfer,
                    transfer_party=transfer_party,
                    debtor_equals_creditor=debtor.id == creditor.id,
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


def build_counterparty_transfer_party(
    debtor: AccountOwner,
    creditor: AccountOwner,
    is_debit_transfer: bool,
) -> TransferParty:
    if is_debit_transfer:
        return _transfer_party_from_owner(creditor)
    else:
        return _transfer_party_from_owner(debtor)


def _transfer_party_from_owner(account_owner: AccountOwner) -> TransferParty:
    party_type = _transfer_party_type_from_owner(account_owner)
    return TransferParty(
        type=party_type,
        id=(
            ANONYMIZED_UUID
            if party_type == TransferPartyType.member
            else account_owner.id
        ),
        name=(
            ANONYMIZED_STR
            if party_type == TransferPartyType.member
            else account_owner.get_name()
        ),
    )


def _transfer_party_type_from_owner(account_owner: AccountOwner) -> TransferPartyType:
    match account_owner:
        case Member():
            return TransferPartyType.member
        case Company():
            return TransferPartyType.company
        case Cooperation():
            return TransferPartyType.cooperation
        case SocialAccounting():
            return TransferPartyType.social_accounting


def construct_plot_data(transfers: list[AccountTransfer]) -> PlotDetails:
    transfers = sorted(transfers, key=lambda transfer: transfer.date)
    return PlotDetails(
        timestamps=[t.date for t in transfers],
        accumulated_volumes=list(accumulate([t.volume for t in transfers])),
    )
