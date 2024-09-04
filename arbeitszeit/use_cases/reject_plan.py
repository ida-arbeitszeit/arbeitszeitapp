from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RejectPlanUseCase:
    @dataclass
    class Request:
        plan: UUID

    @dataclass
    class Response:
        is_rejected: bool = True

    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def reject_plan(self, request: Request) -> Response:
        now = self.datetime_service.now()
        matching_plans = self.database_gateway.get_plans().with_id(request.plan)
        plan = matching_plans.first()
        assert plan
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        if plan.is_rejected:
            return self.Response(is_rejected=False)
        matching_plans.update().set_rejection_date(now).perform()
        return self.Response()
