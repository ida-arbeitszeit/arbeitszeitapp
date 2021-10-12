from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import OfferRepository


@dataclass
class DeleteOfferRequest:
    requesting_company_id: UUID
    offer_id: UUID


@dataclass
class DeleteOfferResponse:
    offer_id: UUID
    is_success: bool


@inject
@dataclass
class DeleteOffer:
    offer_repository: OfferRepository

    def __call__(self, deletion: DeleteOfferRequest) -> DeleteOfferResponse:
        planner = self.offer_repository.get_by_id(deletion.offer_id).plan.planner
        if not planner.id == deletion.requesting_company_id:
            return DeleteOfferResponse(offer_id=deletion.offer_id, is_success=False)
        self.offer_repository.delete_offer(deletion.offer_id)
        return DeleteOfferResponse(offer_id=deletion.offer_id, is_success=True)
