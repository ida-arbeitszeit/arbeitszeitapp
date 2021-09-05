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
        sending_account = sender.account

        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=sending_account,
            receiving_account=plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {plan.id}",
        )
