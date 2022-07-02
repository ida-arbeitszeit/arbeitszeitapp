from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterator, Union
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Company, Member, Purchase, PurposesOfPurchases
from arbeitszeit.repositories import PlanRepository, PurchaseRepository


@dataclass
class PurchaseQueryResponse:
    purchase_date: datetime
    plan_id: UUID
    product_name: str
    product_description: str
    purpose: str
    price_per_unit: Decimal
    amount: int
    price_total: Decimal


@inject
@dataclass
class QueryPurchases:
    purchase_repository: PurchaseRepository
    plan_repository: PlanRepository

    def __call__(
        self,
        user: Union[Member, Company],
    ) -> Iterator[PurchaseQueryResponse]:
        return (
            self._purchase_to_response_model(purchase)
            for purchase in self.purchase_repository.get_purchases_descending_by_date(
                user
            )
        )

    def _purchase_to_response_model(self, purchase: Purchase) -> PurchaseQueryResponse:
        if purchase.purpose == PurposesOfPurchases.means_of_prod:
            purpose = "Prod.mittel"
        elif purchase.purpose == PurposesOfPurchases.raw_materials:
            purpose = "Rohmat."
        else:
            purpose = "Konsum"
        plan_info = self.plan_repository.get_plan_name_and_description(purchase.plan)
        return PurchaseQueryResponse(
            purchase_date=purchase.purchase_date,
            plan_id=purchase.plan,
            product_name=plan_info.name,
            product_description=plan_info.description,
            purpose=purpose,
            price_per_unit=purchase.price_per_unit,
            amount=purchase.amount,
            price_total=purchase.price_per_unit * purchase.amount,
        )
