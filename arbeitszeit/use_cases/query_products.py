from __future__ import annotations

import enum
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from injector import inject

from arbeitszeit.entities import ProductOffer
from arbeitszeit.repositories import CompanyRepository, OfferRepository


class ProductFilter(enum.Enum):
    by_name = enum.auto()
    by_description = enum.auto()


@dataclass
class ProductQueryResponse:
    results: List[QueriedProduct]


@dataclass
class QueriedProduct:
    offer_id: UUID
    seller_name: str
    seller_email: str
    plan_id: str
    product_name: str
    product_description: str
    price_per_unit: Decimal


@inject
@dataclass
class QueryProducts:
    offer_repository: OfferRepository
    company_repository: CompanyRepository

    def __call__(
        self, query: Optional[str], filter_by: ProductFilter
    ) -> ProductQueryResponse:
        if query is None:
            found_offers = self.offer_repository.all_active_offers()
        elif filter_by == ProductFilter.by_name:
            found_offers = self.offer_repository.query_offers_by_name(query)
        else:
            found_offers = self.offer_repository.query_offers_by_description(query)
        results = [self._offer_to_response_model(offer) for offer in found_offers]
        return ProductQueryResponse(
            results=results,
        )

    def _offer_to_response_model(self, offer: ProductOffer) -> QueriedProduct:
        seller = self.offer_repository.get_seller(offer.id)
        return QueriedProduct(
            offer_id=offer.id,
            seller_name=seller.name,
            seller_email=seller.email,
            plan_id=offer.plan_id,
            product_name=offer.name,
            product_description=offer.description,
            price_per_unit=offer.price_per_unit,
        )
