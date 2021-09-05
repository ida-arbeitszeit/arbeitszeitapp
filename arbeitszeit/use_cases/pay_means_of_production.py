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
        plan: Plan,
        pieces: int,
        purpose: PurposesOfPurchases,
    ) -> None:
        assert purpose in (
            PurposesOfPurchases.means_of_prod,
            PurposesOfPurchases.raw_materials,
        ), "Not a valid purpose for this operation."
        if plan.expired:
            raise errors.PlanIsExpired(
                plan=plan,
            )
        if plan.is_public_service:
            raise errors.CompanyCantBuyPublicServices(sender, plan)

        # create transaction
        price_total = pieces * plan.price_per_unit()
        if purpose == PurposesOfPurchases.means_of_prod:
            sending_account = sender.means_account
        elif purpose == PurposesOfPurchases.raw_materials:
            sending_account = sender.raw_material_account

        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=sending_account,
            receiving_account=plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {plan.id}",
        )
