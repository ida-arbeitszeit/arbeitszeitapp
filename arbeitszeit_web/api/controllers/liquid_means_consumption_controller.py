from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.records import ConsumptionType
from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumptionRequest as UseCaseRequest,
)
from arbeitszeit_web.api.controllers.parameters import BodyParameter
from arbeitszeit_web.api.response_errors import BadRequest, Unauthorized
from arbeitszeit_web.json import JsonValue
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session, UserRole

liquid_means_expected_inputs = [
    BodyParameter(
        name="plan_id",
        type=str,
        description="The plan to consume.",
        default=None,
        required=True,
    ),
    BodyParameter(
        name="amount",
        type=int,
        description="The amount of product to consume.",
        default=None,
        required=True,
    ),
]


@dataclass
class LiquidMeansConsumptionController:
    session: Session

    def create_request(self, request: Request) -> UseCaseRequest:
        company = self._validate_current_user()
        json_body = request.get_json()
        return UseCaseRequest(
            consumer=company,
            plan=self._parse_plan_id(json_body),
            amount=self._parse_amount(json_body),
            consumption_type=ConsumptionType.raw_materials,
        )

    def _validate_current_user(self) -> UUID:
        current_user = self.session.get_current_user()
        if current_user is None:
            raise Unauthorized(
                message="You have to authenticate before using this service."
            )
        user_role = self.session.get_user_role()
        if user_role != UserRole.company:
            raise Unauthorized(
                message="You must authenticate as a company to register consumption of means of production."
            )
        return current_user

    def _parse_plan_id(self, json_body: JsonValue) -> UUID:
        if not isinstance(json_body, dict):
            raise BadRequest(message="Plan id missing.")
        plan_id = json_body.get("plan_id")
        if not plan_id:
            raise BadRequest(message="Plan id missing.")
        assert isinstance(plan_id, str)
        try:
            plan_uuid = UUID(plan_id)
        except ValueError:
            raise BadRequest(f"Plan id must be in UUID format, got {plan_id}.")
        return plan_uuid

    def _parse_amount(self, json_body: JsonValue) -> int:
        assert isinstance(json_body, dict)
        amount = json_body.get("amount")
        if not amount:
            raise BadRequest(message="Amount missing.")
        if not isinstance(amount, (int, str, float)):
            raise BadRequest(message=f"Amount must be an integer, got {amount}.")
        try:
            amount_int = int(amount)
        except ValueError:
            raise BadRequest(message=f"Amount must be an integer, got {amount}.")
        if amount_int < 1:
            raise BadRequest(
                message=f"Amount must be a positive integer, got {amount}."
            )
        return amount_int
