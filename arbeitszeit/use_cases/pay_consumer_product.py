from dataclasses import dataclass

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Member, Plan, PurposesOfPurchases
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.repositories import PurchaseRepository, TransactionRepository


@inject
@dataclass
class PayConsumerProduct:
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService
    purchase_factory: PurchaseFactory
    purchase_repository: PurchaseRepository

    def __call__(
        self,
        sender: Member,
        plan: Plan,
        pieces: int,
    ) -> None:
        if not plan.is_active:
            raise errors.PlanIsInactive(
                plan=plan,
            )

        # create purchase
        price_per_unit = plan.price_per_unit()
        purchase = self.purchase_factory.create_purchase(
            purchase_date=self.datetime_service.now(),
            plan=plan,
            buyer=sender,
            price_per_unit=price_per_unit,
            amount=pieces,
            purpose=PurposesOfPurchases.consumption,
        )
        self.purchase_repository.add(purchase)

        # create transaction
        price_total = pieces * plan.price_per_unit()
        sending_account = sender.account

        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=sending_account,
            receiving_account=plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {plan.id}",
        )
