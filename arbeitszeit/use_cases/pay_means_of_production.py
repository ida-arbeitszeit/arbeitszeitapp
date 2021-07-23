from dataclasses import dataclass

from injector import inject

from arbeitszeit import errors
from arbeitszeit.entities import Company, Plan, PurposesOfPurchases
from arbeitszeit.repositories import TransactionRepository
from arbeitszeit.transaction_factory import TransactionFactory

from .adjust_balance import adjust_balance


@inject
@dataclass
class PayMeansOfProduction:
    transaction_repository: TransactionRepository
    transaction_factory: TransactionFactory

    def __call__(
        self,
        sender: Company,
        receiver: Company,
        plan: Plan,
        pieces: int,
        purpose: PurposesOfPurchases,
    ) -> None:
        pass

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

        if not receiver:
            raise errors.CompanyDoesNotExist(
                company=receiver,
            )
        if not plan:
            raise errors.PlanDoesNotExist(
                plan=plan,
            )
        if plan.planner != receiver:
            raise errors.CompanyIsNotPlanner(
                company=receiver,
                planner=plan.planner,
            )

        # reduce balance of buyer
        price_total = pieces * (plan.costs_p + plan.costs_r + plan.costs_a)
        if purpose == PurposesOfPurchases.means_of_prod:
            adjust_balance(
                sender.means_account,
                -price_total,
            )
        elif purpose == PurposesOfPurchases.raw_materials:
            adjust_balance(
                sender.raw_material_account,
                -price_total,
            )

        # increase balance of seller
        adjust_balance(plan.planner.product_account, price_total)

        # create transaction
        if purpose == PurposesOfPurchases.means_of_prod:
            account_from = sender.means_account
        elif purpose == PurposesOfPurchases.means_of_prod:
            account_from = sender.raw_material_account

        transaction = self.transaction_factory.create_transaction(
            account_from=account_from,
            account_to=plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {plan.id}",
        )

        # add transaction to database
        self.transaction_repository.add(transaction)
