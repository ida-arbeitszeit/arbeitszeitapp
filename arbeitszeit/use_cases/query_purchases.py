from dataclasses import dataclass
from typing import Iterator, Union

from injector import inject

from arbeitszeit.entities import Company, Member
from arbeitszeit.repositories import PurchaseRepository


@inject
@dataclass
class QueryPurchases:
    purchase_repository: PurchaseRepository

    def __call__(
        self,
        user: Union[Member, Company],
    ) -> Iterator:
        """returns the user's in-app-purchases, orderd by purchase date, in descending order."""
        return self.purchase_repository.get_purchases_descending_by_date(user)
