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
