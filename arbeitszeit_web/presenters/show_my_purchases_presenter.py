from dataclasses import dataclass
from datetime import datetime
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
        price_per_unit: Decimal
        amount: int
        price_total: Decimal
    
    purchases: list

    def append(self, purchase_respond: PurchaseQueryResponse):
        p = self.Purchase(
            purchase_date=purchase_respond.purchase_date,  # format_datetime(zone='Europe/Berlin', fmt='%d.%m.%Y')
            product_name=purchase_respond.product_name,
            product_description=purchase_respond.product_description,
            price_per_unit=purchase_respond.price_per_unit,
            amount=purchase_respond.amount,
            price_total=purchase_respond.price_total,
        )
        self.purchases.append(p)

    # us from typing import List ?? see ShowPAccountDetailsPresenter
    def __len__(self):
        return len(self.purchases)

    def __iter__(self):
        for i in self.purchases:
            yield i


class ShowMyPurchasesPresenter:
    def present(self, use_case_response: Iterator[PurchaseQueryResponse]) -> ViewModel:
        
        model = ViewModel([])

        for p in use_case_response:
            model.append(p)

        return model
        """
        return ViewModel(
            purchase_date=use_case_response.purchase_date,
            product_name=use_case_response.product_name,
            product_description=use_case_response.product_description,
            price_per_unit=use_case_response.price_per_unit,
            amount=use_case_response.amount,
            price_total=use_case_response.price_total,
        )
        """
