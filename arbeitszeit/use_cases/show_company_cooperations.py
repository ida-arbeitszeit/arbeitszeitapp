from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Plan
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    company: UUID


@dataclass
class InboundCoopRequest:
    coop_id: UUID
    coop_name: str
    plan_id: UUID
    plan_name: str
    planner_name: str
    planner_id: UUID


@dataclass
class OutboundCoopRequest:
    plan_id: UUID
    plan_name: str
    coop_id: UUID
    coop_name: str


@dataclass
class Response:
    inbound_cooperation_requests: List[InboundCoopRequest]
    outbound_cooperation_requests: List[OutboundCoopRequest]


@dataclass
class ShowCompanyCooperationsUseCase:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def show_company_cooperations(self, request: Request) -> Response:
        now = self.datetime_service.now()
        inbound_cooperation_requests = [
            self._plan_to_inbound_coop_request(plan)
            for plan in self.database_gateway.get_plans()
            .that_request_cooperation_with_coordinator(request.company)
            .that_will_expire_after(now)
        ]
        plans_with_open_requests = (
            self.database_gateway.get_plans()
            .planned_by(request.company)
            .with_open_cooperation_request()
            .that_will_expire_after(now)
        )
        outbound_cooperation_requests = [
            self._plan_to_outbound_coop_request(plan)
            for plan in plans_with_open_requests
        ]
        return Response(
            inbound_cooperation_requests=inbound_cooperation_requests,
            outbound_cooperation_requests=outbound_cooperation_requests,
        )

    def _plan_to_outbound_coop_request(self, plan: Plan) -> OutboundCoopRequest:
        assert plan.requested_cooperation
        requested_cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(plan.requested_cooperation)
            .first()
        )
        assert requested_cooperation
        return OutboundCoopRequest(
            plan_id=plan.id,
            plan_name=plan.prd_name,
            coop_id=plan.requested_cooperation,
            coop_name=requested_cooperation.name,
        )

    def _company_exists(self, request: Request) -> bool:
        return bool(self.database_gateway.get_companies().with_id(request.company))

    def _plan_to_inbound_coop_request(self, plan: Plan) -> InboundCoopRequest:
        assert plan.requested_cooperation
        requested_cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(plan.requested_cooperation)
            .first()
        )
        assert requested_cooperation
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        return InboundCoopRequest(
            coop_id=plan.requested_cooperation,
            coop_name=requested_cooperation.name,
            plan_id=plan.id,
            plan_name=plan.prd_name,
            planner_name=planner.name,
            planner_id=planner.id,
        )
