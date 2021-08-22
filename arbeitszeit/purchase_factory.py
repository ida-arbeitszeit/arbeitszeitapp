from datetime import datetime
from decimal import Decimal
from typing import Union

from .entities import Company, Member, ProductOffer, Purchase, PurposesOfPurchases


class PurchaseFactory:
    def create_private_purchase(
        self,
        purchase_date: datetime,
        product_offer: ProductOffer,
        buyer: Union[Member, Company],
        price_per_unit: Decimal,
        amount: int,
        purpose: PurposesOfPurchases,
    ) -> Purchase:
        return Purchase(
            purchase_date=purchase_date,
            product_offer=product_offer,
            buyer=buyer,
            price_per_unit=price_per_unit,
            amount=amount,
            purpose=purpose,
        )
