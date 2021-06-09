from datetime import datetime
from decimal import Decimal
from typing import Union
from enum import Enum

from arbeitszeit.entities import Company, Member, ProductOffer, Purchase


class PurposesOfPurchases(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"


class PurchaseFactory:
    def create_private_purchase(
        self,
        purchase_date: datetime,
        product_offer: ProductOffer,
        buyer: Union[Member, Company],
        price: Decimal,
        amount: int,
        purpose: PurposesOfPurchases,
    ) -> Purchase:
        return Purchase(
            purchase_date=purchase_date,
            product_offer=product_offer,
            buyer=buyer,
            price=price,
            amount=amount,
            purpose=purpose,
        )
