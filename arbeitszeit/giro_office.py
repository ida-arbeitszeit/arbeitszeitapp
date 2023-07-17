import enum
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Member, Transaction
from arbeitszeit.repositories import DatabaseGateway


class TransactionRejection(Exception, enum.Enum):
    insufficient_account_balance = enum.auto()


@dataclass
class GiroOffice:
    """Conduct certificate transactions from one account to another."""

    control_thresholds: ControlThresholds
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def record_transaction_from_member(
        self,
        sender: Member,
        receiving_account: UUID,
        amount_sent: Decimal,
        amount_received: Decimal,
        purpose: str,
    ) -> Transaction:
        sending_account = sender.account
        if not self._is_account_balance_sufficient(amount_sent, sending_account):
            raise TransactionRejection.insufficient_account_balance
        return self.database_gateway.create_transaction(
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
        account_balance = self._get_account_balance(sending_account)
        if account_balance is None:
            return False
        elif transaction_volume > account_balance + allowed_overdraw:
            return False
        return True

    def _get_account_balance(self, account: UUID) -> Optional[Decimal]:
        result = (
            self.database_gateway.get_accounts()
            .with_id(account)
            .joined_with_balance()
            .first()
        )
        if result:
            return result[1]
        else:
            return None
