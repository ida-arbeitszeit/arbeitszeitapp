from __future__ import annotations

from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit import records
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ListMyCooperatingPlansUseCase:
    @dataclass
    class Request:
        company: UUID

    @dataclass
    class CooperatingPlan:
        plan_id: UUID
        plan_name: str
        coop_id: UUID
        coop_name: str

    @dataclass
    class Response:
        cooperating_plans: List[ListMyCooperatingPlansUseCase.CooperatingPlan]

    class Failure(Exception):
        pass

    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def list_cooperations(self, request: Request) -> Response:
        if not self.database_gateway.get_companies().with_id(request.company):
            raise self.Failure()
        now = self.datetime_service.now()
        plans = (
            self.database_gateway.get_plans()
            .that_will_expire_after(now)
            .that_were_activated_before(now)
            .planned_by(request.company)
            .that_are_cooperating()
        )
        return self.Response(
            cooperating_plans=[
                self._create_plan_object(plan, cooperation)
                for plan, cooperation in plans.joined_with_cooperation()
                if cooperation
            ]
        )

    def _create_plan_object(
        self, plan: records.Plan, cooperation: records.Cooperation
    ) -> CooperatingPlan:
        return self.CooperatingPlan(
            plan_id=plan.id,
            plan_name=plan.prd_name,
            coop_id=cooperation.id,
            coop_name=cooperation.name,
        )
