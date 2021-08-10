from dataclasses import dataclass

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Member, Plan
from arbeitszeit.repositories import TransactionRepository


@inject
@dataclass
class PayConsumerProduct:
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService

    def __call__(
        self,
        sender: Member,
        receiver: Company,
        plan: Plan,
        pieces: int,
    ) -> None:
        pass

        """
        This function enables the payment of consumer products which were *not* bought
        on the app's marketplace. Apart from sender and receiver it has to be specified
        the seller's plan and the amount of pieces to be paid.

        This function
            - adjusts the balances of the buying member and the selling company
            - adds the transaction to the repository
        """
        if plan.planner != receiver:
            raise errors.CompanyIsNotPlanner(
                company=receiver,
                planner=plan.planner,
            )
        if plan.expired:
            raise errors.PlanIsExpired(
                plan=plan,
            )

        # create transaction
        price_total = pieces * plan.production_costs.total_cost()
        account_from = sender.account

        transaction = self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            account_from=account_from,
            account_to=plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {plan.id}",
        )

        # adjust balances
        transaction.adjust_balances()
