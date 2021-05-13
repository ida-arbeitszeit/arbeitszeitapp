from datetime import datetime
from decimal import Decimal
from typing import Union

from arbeitszeit.entities import Company, Member, ProductOffer, Purchase


class PurchaseFactory:
    def create_private_purchase(
        self,
        purchase_date: datetime,
        product_offer: ProductOffer,
        buyer: Union[Member, Company],
        price: Decimal,
    ) -> Purchase:
        return Purchase(
            purchase_date=purchase_date,
            product_offer=product_offer,
            buyer=buyer,
            price=price,
        )
