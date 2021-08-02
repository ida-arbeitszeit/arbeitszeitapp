from dataclasses import dataclass

from injector import inject

from arbeitszeit import errors
from arbeitszeit.entities import Company, Member, Plan
from arbeitszeit.repositories import TransactionRepository
from arbeitszeit.transaction_factory import TransactionFactory


@inject
@dataclass
class PayConsumerProduct:
    transaction_repository: TransactionRepository
    transaction_factory: TransactionFactory

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
        price_total = pieces * (plan.costs_p + plan.costs_r + plan.costs_a)
        account_from = sender.account

        transaction = self.transaction_factory.create_transaction(
            account_from=account_from,
            account_to=plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {plan.id}",
        )

        # add transaction to database
        self.transaction_repository.add(transaction)

        # adjust balances
        transaction.adjust_balances()
