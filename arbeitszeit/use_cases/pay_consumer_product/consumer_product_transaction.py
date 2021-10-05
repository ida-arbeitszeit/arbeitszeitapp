from __future__ import annotations

from dataclasses import dataclass

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Member, Plan, PurposesOfPurchases
from arbeitszeit.repositories import PurchaseRepository, TransactionRepository


@inject
@dataclass
class ConsumerProductTransactionFactory:
    datetime_service: DatetimeService
    purchase_repository: PurchaseRepository
    transaction_repository: TransactionRepository

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
        )


@dataclass
class ConsumerProductTransaction:
    buyer: Member
    plan: Plan
    amount: int
    datetime_service: DatetimeService
    purchase_repository: PurchaseRepository
    transaction_repository: TransactionRepository

    def record_purchase(self) -> None:
        price_per_unit = self.plan.price_per_unit
        self.purchase_repository.create_purchase(
            purchase_date=self.datetime_service.now(),
            plan=self.plan,
            buyer=self.buyer,
            price_per_unit=price_per_unit,
            amount=self.amount,
            purpose=PurposesOfPurchases.consumption,
        )

    def exchange_currency(self) -> None:
        price_total = self.amount * self.plan.price_per_unit
        sending_account = self.buyer.account
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=sending_account,
            receiving_account=self.plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {self.plan.id}",
        )
