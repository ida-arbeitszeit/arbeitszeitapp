from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import ProductOffer
from arbeitszeit.repositories import OfferRepository, PlanRepository


@dataclass
class CreateOfferRequest:
    name: str
    description: str
    plan_id: UUID


@inject
@dataclass
class CreateOffer:
    offer_repository: OfferRepository
    plan_repository: PlanRepository
    datetime_service: DatetimeService

    def __call__(self, offer: CreateOfferRequest) -> ProductOffer:
        plan = self.plan_repository.get_plan_by_id(offer.plan_id)
        return self.offer_repository.create_offer(
            plan,
            self.datetime_service.now(),
            offer.name,
            offer.description,
        )
