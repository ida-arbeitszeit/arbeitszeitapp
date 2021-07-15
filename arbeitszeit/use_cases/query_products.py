import enum
from dataclasses import dataclass
from typing import Optional

from injector import inject

from arbeitszeit.repositories import OfferRepository


class ProductFilter(enum.Enum):
    by_name = enum.auto()
    by_description = enum.auto()


@inject
@dataclass
class QueryProducts:
    offer_repository: OfferRepository

    def __call__(self, query: Optional[str], filter_by: ProductFilter):
        if query is None:
            return self.offer_repository.all_active_offers()
        if filter_by == ProductFilter.by_name:
            return self.offer_repository.query_offers_by_name(query)
        else:
            return self.offer_repository.query_offers_by_description(query)
