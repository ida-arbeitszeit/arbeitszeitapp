from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import (
    CompanyRepository,
    MetaProductRepository,
)


@dataclass
class CreateMetaProductRequest:
    coordinator_id: UUID
    name: str
    definition: str


@dataclass
class CreateMetaProductResponse:
    meta_product_id: UUID


@inject
@dataclass
class CreateMetaProduct:
    company_repository: CompanyRepository
    meta_product_repository: MetaProductRepository
    datetime_service: DatetimeService

    def __call__(
        self, request: CreateMetaProductRequest
    ) -> Optional[CreateMetaProductResponse]:
        coordinator = self.company_repository.get_by_id(request.coordinator_id)
        if coordinator is None:
            return None
        meta_product = self.meta_product_repository.create_meta_product(
            self.datetime_service.now(),
            request.name,
            request.definition,
            coordinator,
        )
        return CreateMetaProductResponse(meta_product_id=meta_product.id)
