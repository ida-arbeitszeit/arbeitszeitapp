from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import OfferRepository, PlanRepository


@dataclass
class CreateOfferRequest:
    name: str
    description: str
    plan_id: UUID


@dataclass
class CreateOfferResponse:
    id: UUID
    name: str
    description: str


@inject
@dataclass
class CreateOffer:
    offer_repository: OfferRepository
    plan_repository: PlanRepository
    datetime_service: DatetimeService

    def __call__(self, offer_request: CreateOfferRequest) -> CreateOfferResponse:
        plan = self.plan_repository.get_plan_by_id(offer_request.plan_id)
        offer = self.offer_repository.create_offer(
            plan,
            self.datetime_service.now(),
            offer_request.name,
            offer_request.description,
        )
        return CreateOfferResponse(
            id=offer.id,
            name=offer.name,
            description=offer.description,
        )
