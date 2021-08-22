from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterator, Union
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Company, Member, Purchase, PurposesOfPurchases
from arbeitszeit.repositories import PurchaseRepository


@dataclass
class PurchaseQueryResponse:
    purchase_date: datetime
    offer_id: UUID
    product_name: str
    product_description: str
    purpose: PurposesOfPurchases
    price_per_unit: Decimal
    amount: int
    price_total: Decimal


@inject
@dataclass
class QueryPurchases:
    purchase_repository: PurchaseRepository

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
        return PurchaseQueryResponse(
            purchase_date=purchase.purchase_date,
            offer_id=purchase.product_offer.id,
            product_name=purchase.product_offer.name,
            product_description=purchase.product_offer.description,
            purpose=purchase.purpose,
            price_per_unit=purchase.price_per_unit,
            amount=purchase.amount,
            price_total=purchase.price_per_unit * purchase.amount,
        )
