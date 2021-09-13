from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import OfferRepository, PlanRepository


@dataclass
class CreateOfferRequest:
    name: str
    description: str
    plan_id: str
    seller: UUID
    price_per_unit: Decimal


@dataclass
class CreateOfferResponse:
    name: str
    description: str


@inject
@dataclass
class CreateOffer:
    offer_repository: OfferRepository
    plan_repository: PlanRepository
    datetime_service: DatetimeService

    def __call__(self, offer: CreateOfferRequest) -> CreateOfferResponse:
        self.offer_repository.create_offer(
            offer.plan_id,
            self.datetime_service.now(),
            offer.name,
            offer.description,
            offer.seller,
            offer.price_per_unit,
        )
        return CreateOfferResponse(
            name=offer.name,
            description=offer.description,
        )
