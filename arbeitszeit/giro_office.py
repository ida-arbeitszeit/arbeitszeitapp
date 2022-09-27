from __future__ import annotations

from dataclasses import dataclass

from injector import inject

from arbeitszeit import repositories
from arbeitszeit.actors import (
    ConsumerProductTransaction,
    TransactionReceipt,
    TransactionRejection,
)
from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.price_calculator import calculate_price


@inject
@dataclass
class GiroOfficeImpl:
    plan_cooperation_repository: repositories.PlanCooperationRepository
    datetime_service: DatetimeService
    purchase_repository: repositories.PurchaseRepository
    transaction_repository: repositories.TransactionRepository
    control_thresholds: ControlThresholds
    account_repository: repositories.AccountRepository

    def conduct_consumer_transaction(
        self, transaction: ConsumerProductTransaction
    ) -> TransactionReceipt:
        if not self._is_account_balance_sufficient(transaction):
            return TransactionReceipt(
                rejection_reason=TransactionRejection.insufficient_balance,
            )
        self._record_purchase(transaction)
        self._exchange_currency(transaction)
        return TransactionReceipt(rejection_reason=None)

    def _record_purchase(self, transaction: ConsumerProductTransaction) -> None:
        price_per_unit = calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(transaction.plan.id)
        )
        self.purchase_repository.create_purchase_by_member(
            purchase_date=self.datetime_service.now(),
            plan=transaction.plan.id,
            buyer=transaction.buyer.id,
            price_per_unit=price_per_unit,
            amount=transaction.amount,
        )

    def _exchange_currency(self, transaction: ConsumerProductTransaction) -> None:
        coop_price = transaction.amount * calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(transaction.plan.id)
        )
        individual_price = transaction.amount * calculate_price([transaction.plan])
        sending_account = transaction.buyer.account
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=sending_account,
            receiving_account=transaction.plan.planner.product_account,
            amount_sent=coop_price,
            amount_received=individual_price,
            purpose=f"Plan-Id: {transaction.plan.id}",
        )

    def _is_account_balance_sufficient(
        self, transaction: ConsumerProductTransaction
    ) -> bool:
        allowed_overdraw = (
            self.control_thresholds.get_allowed_overdraw_of_member_account()
        )
        account_balance = self.account_repository.get_account_balance(
            transaction.buyer.account
        )
        price = transaction.amount * calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(transaction.plan.id)
        )
        if price == 0:
            return True
        if (account_balance - price + allowed_overdraw) < 0:
            return False
        return True
