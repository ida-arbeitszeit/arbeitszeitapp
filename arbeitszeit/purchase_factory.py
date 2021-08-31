from datetime import datetime
from decimal import Decimal
from typing import Union

from .entities import Company, Member, Plan, Purchase, PurposesOfPurchases


class PurchaseFactory:
    def create_purchase(
        self,
        purchase_date: datetime,
        plan: Plan,
        buyer: Union[Member, Company],
        price_per_unit: Decimal,
        amount: int,
        purpose: PurposesOfPurchases,
    ) -> Purchase:
        return Purchase(
            purchase_date=purchase_date,
            plan=plan,
            buyer=buyer,
            price_per_unit=price_per_unit,
            amount=amount,
            purpose=purpose,
        )
