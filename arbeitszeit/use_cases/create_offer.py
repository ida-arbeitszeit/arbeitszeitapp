from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from injector import inject
from arbeitszeit.errors import PlanIsInactive

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import OfferRepository, PlanRepository
from enum import Enum, auto


class RejectionReason(Enum):
    plan_inactive = auto()


@dataclass
class CreateOfferRequest:
    name: str
    description: str
    plan_id: UUID


@dataclass
class CreateOfferResponse:
    id: Optional[UUID]
    name: Optional[str]
    description: Optional[str]
    rejection_reason: Optional[RejectionReason]

    @property
    def is_created(self) -> bool:
        return self.rejection_reason is None


@inject
@dataclass
class CreateOffer:
    offer_repository: OfferRepository
    plan_repository: PlanRepository
    datetime_service: DatetimeService

    def __call__(self, offer_request: CreateOfferRequest) -> CreateOfferResponse:
        try:
            return self._perform_create_offer(offer_request)
        except PlanIsInactive:
            return CreateOfferResponse(
                id=None,
                name=None,
                description=None,
                rejection_reason=RejectionReason.plan_inactive,
            )

    def _perform_create_offer(
        self, offer_request: CreateOfferRequest
    ) -> CreateOfferResponse:
        plan = self.plan_repository.get_plan_by_id(offer_request.plan_id)
        if not plan.is_active:
            raise PlanIsInactive(plan)
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
            rejection_reason=None,
        )
