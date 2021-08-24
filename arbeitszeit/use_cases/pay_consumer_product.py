from dataclasses import dataclass

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Member, Plan
from arbeitszeit.repositories import TransactionRepository


@inject
@dataclass
class PayConsumerProduct:
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService

    def __call__(
        self,
        sender: Member,
        plan: Plan,
        pieces: int,
    ) -> None:
        if plan.expired:
            raise errors.PlanIsExpired(
                plan=plan,
            )

        # create transaction
        price_total = pieces * plan.price_per_unit()
        account_from = sender.account

        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            account_from=account_from,
            account_to=plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {plan.id}",
        )
