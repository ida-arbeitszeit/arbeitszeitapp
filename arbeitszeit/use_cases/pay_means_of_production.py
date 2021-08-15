from dataclasses import dataclass

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Plan, PurposesOfPurchases
from arbeitszeit.repositories import TransactionRepository


@inject
@dataclass
class PayMeansOfProduction:
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService

    def __call__(
        self,
        sender: Company,
        receiver: Company,
        plan: Plan,
        pieces: int,
        purpose: PurposesOfPurchases,
    ) -> None:
        """
        This function enables the payment of means of production
        or raw materials which were *not* bought on the app's marketplace.
        Apart from sender and receiver it has to be specified the amount
        of pieces to be paid, the seller's plan and the purpose of the purchase.

        What this function does:
            - It adjusts the balances of the buying company and the selling company
            - It adds the transaction to the repository
        """
        assert purpose in (
            PurposesOfPurchases.means_of_prod,
            PurposesOfPurchases.raw_materials,
        ), "Not a valid purpose for this operation."

        if plan.planner != receiver:
            raise errors.CompanyIsNotPlanner(
                company=receiver,
                planner=plan.planner,
            )

        # create transaction
        price_total = pieces * plan.cost_per_unit()
        if purpose == PurposesOfPurchases.means_of_prod:
            account_from = sender.means_account
        elif purpose == PurposesOfPurchases.raw_materials:
            account_from = sender.raw_material_account

        transaction = self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            account_from=account_from,
            account_to=plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {plan.id}",
        )

        # adjust balances
        transaction.adjust_balances()
