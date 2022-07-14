from dataclasses import dataclass, field
from datetime import datetime
from arbeitszeit_flask.datetime import RealtimeDatetimeService
from decimal import Decimal
from arbeitszeit.use_cases.query_purchases import PurchaseQueryResponse
from typing import Iterator


@dataclass
class ViewModel:
    @dataclass
    class Purchase:
        purchase_date: datetime
        product_name: str
        product_description: str
        price_per_unit: str
        amount: int
        price_total: str
    
    purchases: list[Purchase] = field(default_factory=list)
    
    def append(self, purchase_respond: PurchaseQueryResponse):
        
        p = self.Purchase(
            #purchase_date=purchase_respond.purchase_date,  # format_datetime(zone='Europe/Berlin', fmt='%d.%m.%Y')
            purchase_date=RealtimeDatetimeService().
                    format_datetime(date=purchase_respond.purchase_date),
            product_name=purchase_respond.product_name,
            product_description=purchase_respond.product_description,
            price_per_unit=round(purchase_respond.price_per_unit, 2),
            amount=purchase_respond.amount,
            price_total=round(purchase_respond.price_total, 2),
        )
        self.purchases.append(p)

    def __len__(self):
        return len(self.purchases)

    def __iter__(self):
        for i in self.purchases:
            yield i


class ShowMyPurchasesPresenter:
    def present(self, use_case_response: Iterator[PurchaseQueryResponse]) -> ViewModel:
        
        model = ViewModel()

        for p in use_case_response:
            model.append(p)

        return model

