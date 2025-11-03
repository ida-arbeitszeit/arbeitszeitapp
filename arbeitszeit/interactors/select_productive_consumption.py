from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import ConsumptionType
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    plan_id: UUID | None
    amount: int | None
    consumption_type: ConsumptionType | None


@dataclass
class NoPlanResponse:
    amount: int | None
    consumption_type: ConsumptionType | None


@dataclass
class InvalidPlanResponse:
    amount: int | None
    consumption_type: ConsumptionType | None


@dataclass
class ValidPlanResponse:
    plan_id: UUID
    amount: int | None
    consumption_type: ConsumptionType | None
    plan_name: str
    plan_description: str


@dataclass
class SelectProductiveConsumptionInteractor:
    database: DatabaseGateway
    datetime_service: DatetimeService

    def select_productive_consumption(
        self, request: Request
    ) -> NoPlanResponse | InvalidPlanResponse | ValidPlanResponse:
        amount = request.amount
        consumption_type = request.consumption_type
        if not request.plan_id:
            return NoPlanResponse(
                amount=amount,
                consumption_type=consumption_type,
            )
        plan_result = (
            self.database.get_plans()
            .with_id(request.plan_id)
            .that_will_expire_after(self.datetime_service.now())
        )
        if not plan_result:
            return InvalidPlanResponse(
                amount=amount,
                consumption_type=consumption_type,
            )
        plan = plan_result.first()
        assert plan
        return ValidPlanResponse(
            plan_id=request.plan_id,
            amount=amount,
            consumption_type=consumption_type,
            plan_name=plan.prd_name,
            plan_description=plan.description,
        )
