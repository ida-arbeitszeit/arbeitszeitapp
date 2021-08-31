from dataclasses import dataclass

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Plan, PurposesOfPurchases
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.repositories import PurchaseRepository, TransactionRepository


@inject
@dataclass
class PayMeansOfProduction:
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService
    purchase_factory: PurchaseFactory
    purchase_repository: PurchaseRepository

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

        # create purchase
        price_per_unit = plan.price_per_unit()
        purchase = self.purchase_factory.create_purchase(
            purchase_date=self.datetime_service.now(),
            plan=plan,
            buyer=sender,
            price_per_unit=price_per_unit,
            amount=pieces,
            purpose=purpose,
        )
        self.purchase_repository.add(purchase)

        # create transaction
        price_total = pieces * plan.price_per_unit()
        if purpose == PurposesOfPurchases.means_of_prod:
            account_from = sender.means_account
        elif purpose == PurposesOfPurchases.raw_materials:
            account_from = sender.raw_material_account

        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            account_from=account_from,
            account_to=plan.planner.product_account,
            amount=price_total,
            purpose=f"Plan-Id: {plan.id}",
        )
