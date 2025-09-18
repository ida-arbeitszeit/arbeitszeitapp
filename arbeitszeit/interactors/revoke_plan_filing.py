from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RevokePlanFilingInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    @dataclass
    class Request:
        requester: UUID
        plan: UUID

    @dataclass
    class Response:
        class RejectionReason(Exception, Enum):
            requester_not_found = auto()
            plan_not_found = auto()
            requester_is_not_planner = auto()
            plan_is_active = auto()
            plan_is_expired = auto()

        rejection_reason: Optional[RejectionReason]
        plan_draft: Optional[UUID]

        @property
        def is_rejected(self) -> bool:
            return self.rejection_reason is not None

    def revoke_plan_filing(self, request: Request) -> Response:
        rejection_reason = self._validate_request(request)
        if rejection_reason:
            return self.Response(rejection_reason=rejection_reason, plan_draft=None)
        draft = self._create_draft_with_the_revoked_plan_attributes(request)
        self._delete_plan(request)
        return self.Response(rejection_reason=None, plan_draft=draft)

    def _validate_request(self, request: Request) -> Optional[Response.RejectionReason]:
        now = self.datetime_service.now()
        requesting_company = (
            self.database_gateway.get_companies().with_id(request.requester).first()
        )
        plan = self.database_gateway.get_plans().with_id(request.plan).first()
        if not requesting_company:
            return self.Response.RejectionReason.requester_not_found
        if not plan:
            return self.Response.RejectionReason.plan_not_found
        if plan.planner != requesting_company.id:
            return self.Response.RejectionReason.requester_is_not_planner
        if plan.is_approved and not plan.is_expired_as_of(now):
            return self.Response.RejectionReason.plan_is_active
        if plan.is_expired_as_of(now):
            return self.Response.RejectionReason.plan_is_expired
        return None

    def _delete_plan(self, request: Request) -> None:
        self.database_gateway.get_plans().with_id(request.plan).delete()

    def _create_draft_with_the_revoked_plan_attributes(self, request: Request) -> UUID:
        plan = self.database_gateway.get_plans().with_id(request.plan).first()
        assert plan
        draft = self.database_gateway.create_plan_draft(
            planner=plan.planner,
            product_name=plan.prd_name,
            description=plan.description,
            costs=plan.production_costs,
            production_unit=plan.prd_unit,
            amount=plan.prd_amount,
            timeframe_in_days=plan.timeframe,
            is_public_service=plan.is_public_service,
            creation_timestamp=plan.plan_creation_date,
        )
        return draft.id
