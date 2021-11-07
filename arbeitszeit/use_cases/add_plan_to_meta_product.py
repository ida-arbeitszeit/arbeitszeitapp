from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import MetaProductRepository, PlanRepository


@dataclass
class AddPlanToMetaProductRequest:
    plan_id: UUID
    meta_product_id: UUID


@dataclass
class AddPlanToMetaProductResponse:
    class RejectionReason(Exception, Enum):
        plan_not_found = auto()
        meta_product_not_found = auto()
        plan_inactive = auto()
        plan_has_meta_product = auto()
        plan_already_part_of_meta_product = auto()
        plan_is_public_service = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@inject
@dataclass
class AddPlanToMetaProduct:
    plan_repository: PlanRepository
    meta_product_repository: MetaProductRepository

    def __call__(
        self, request: AddPlanToMetaProductRequest
    ) -> AddPlanToMetaProductResponse:
        try:
            self._validate_request(request)
        except AddPlanToMetaProductResponse.RejectionReason as reason:
            return AddPlanToMetaProductResponse(rejection_reason=reason)

        self.meta_product_repository.add_plan_to_meta_product(
            request.plan_id, request.meta_product_id
        )
        self.meta_product_repository.add_meta_product_to_plan(
            request.plan_id, request.meta_product_id
        )
        return AddPlanToMetaProductResponse(rejection_reason=None)

    def _validate_request(self, request: AddPlanToMetaProductRequest) -> None:
        plan = self.plan_repository.get_plan_by_id(request.plan_id)
        meta_product = self.meta_product_repository.get_by_id(request.meta_product_id)
        if plan is None:
            raise AddPlanToMetaProductResponse.RejectionReason.plan_not_found
        if meta_product is None:
            raise AddPlanToMetaProductResponse.RejectionReason.meta_product_not_found
        if not plan.is_active:
            raise AddPlanToMetaProductResponse.RejectionReason.plan_inactive
        if plan.meta_product:
            raise AddPlanToMetaProductResponse.RejectionReason.plan_has_meta_product
        if plan in meta_product.plans:
            raise AddPlanToMetaProductResponse.RejectionReason.plan_already_part_of_meta_product
        if plan.is_public_service:
            raise AddPlanToMetaProductResponse.RejectionReason.plan_is_public_service
