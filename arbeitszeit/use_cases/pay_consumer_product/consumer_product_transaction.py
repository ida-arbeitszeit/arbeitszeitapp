from __future__ import annotations

from dataclasses import dataclass

from injector import inject

from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Member, Plan, PurposesOfPurchases
from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.repositories import (
    AccountRepository,
    PlanCooperationRepository,
    PurchaseRepository,
    TransactionRepository,
)


@inject
@dataclass
class ConsumerProductTransactionFactory:
    datetime_service: DatetimeService
    purchase_repository: PurchaseRepository
    transaction_repository: TransactionRepository
    plan_cooperation_repository: PlanCooperationRepository
    account_repository: AccountRepository
    control_thresholds: ControlThresholds

    def create_consumer_product_transaction(
        self,
        buyer: Member,
        plan: Plan,
        amount: int,
    ) -> ConsumerProductTransaction:
        return ConsumerProductTransaction(
            buyer,
            plan,
            amount,
            self.datetime_service,
            self.purchase_repository,
            self.transaction_repository,
            self.plan_cooperation_repository,
            self.account_repository,
            self.control_thresholds,
        )


@dataclass
class ConsumerProductTransaction:
    buyer: Member
    plan: Plan
    amount: int
    datetime_service: DatetimeService
    purchase_repository: PurchaseRepository
    transaction_repository: TransactionRepository
    plan_cooperation_repository: PlanCooperationRepository
    account_repository: AccountRepository
    control_thresholds: ControlThresholds

    def is_account_balance_sufficient(self) -> bool:
        allowed_overdraw = (
            self.control_thresholds.get_allowed_overdraw_of_member_account()
        )
        account_balance = self.account_repository.get_account_balance(
            self.buyer.account
        )
        price = self.amount * calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(self.plan.id)
        )
        if price == 0:
            return True
        if (account_balance - price + allowed_overdraw) < 0:
            return False
        return True

    def record_purchase(self) -> None:
        price_per_unit = calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(self.plan.id)
        )
        self.purchase_repository.create_purchase(
            purchase_date=self.datetime_service.now(),
            plan=self.plan,
            buyer=self.buyer,
            price_per_unit=price_per_unit,
            amount=self.amount,
            purpose=PurposesOfPurchases.consumption,
        )

    def exchange_currency(self) -> None:
        coop_price = self.amount * calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(self.plan.id)
        )
        individual_price = self.amount * calculate_price([self.plan])
        sending_account = self.buyer.account
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=sending_account,
            receiving_account=self.plan.planner.product_account,
            amount_sent=coop_price,
            amount_received=individual_price,
            purpose=f"Plan-Id: {self.plan.id}",
        )
