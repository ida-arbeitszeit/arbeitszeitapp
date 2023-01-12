import enum
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from injector import inject

from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Member
from arbeitszeit.repositories import AccountRepository, TransactionRepository


class TransactionRejection(Exception, enum.Enum):
    insufficient_account_balance = enum.auto()


@inject
@dataclass
class GiroOffice:
    """Conduct certificate transactions from one account to another."""

    account_repository: AccountRepository
    control_thresholds: ControlThresholds
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService

    def record_transaction_from_member(
        self,
        sender: Member,
        receiving_account: UUID,
        amount_sent: Decimal,
        amount_received: Decimal,
        purpose: str,
    ) -> None:
        sending_account = sender.account
        if not self._is_account_balance_sufficient(amount_sent, sending_account):
            raise TransactionRejection.insufficient_account_balance
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=sending_account,
            receiving_account=receiving_account,
            amount_sent=amount_sent,
            amount_received=amount_received,
            purpose=purpose,
        )

    def _is_account_balance_sufficient(
        self, transaction_volume: Decimal, sending_account: UUID
    ) -> bool:
        if transaction_volume <= 0:
            return True
        allowed_overdraw = (
            self.control_thresholds.get_allowed_overdraw_of_member_account()
        )
        account_balance = self.account_repository.get_account_balance(sending_account)
        print(account_balance, transaction_volume, allowed_overdraw)
        if transaction_volume > account_balance + allowed_overdraw:
            return False
        return True
