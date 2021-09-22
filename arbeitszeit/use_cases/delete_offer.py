from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import OfferRepository


@dataclass
class DeleteOfferResponse:
    offer_id: UUID


@inject
@dataclass
class DeleteOffer:
    offer_repository: OfferRepository

    def __call__(self, offer_id: UUID) -> DeleteOfferResponse:
        self.offer_repository.delete_offer(offer_id)
        return DeleteOfferResponse(offer_id=offer_id)
