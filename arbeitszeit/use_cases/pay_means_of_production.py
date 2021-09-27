from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.repositories import (
    CompanyRepository,
    PlanRepository,
    PurchaseRepository,
    TransactionRepository,
)


@dataclass
class PayMeansOfProductionRequest:
    buyer: UUID
    plan: UUID
    amount: int
    purpose: PurposesOfPurchases


@inject
@dataclass
class PayMeansOfProduction:
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService
    purchase_factory: PurchaseFactory
    purchase_repository: PurchaseRepository
    plan_repository: PlanRepository
    company_repository: CompanyRepository

    def __call__(self, request: PayMeansOfProductionRequest) -> None:
        plan = self.plan_repository.get_plan_by_id(request.plan)
        sender = self.company_repository.get_by_id(request.buyer)
        purpose = request.purpose
        pieces = request.amount
        assert purpose in (
            PurposesOfPurchases.means_of_prod,
            PurposesOfPurchases.raw_materials,
        ), "Not a valid purpose for this operation."
        if not plan.is_active:
            raise errors.PlanIsInactive(
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
