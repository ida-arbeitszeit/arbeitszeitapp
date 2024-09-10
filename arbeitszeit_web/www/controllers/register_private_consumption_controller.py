from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumptionRequest,
)
from arbeitszeit_web.forms import RegisterPrivateConsumptionForm
from arbeitszeit_web.request import Request
from arbeitszeit_web.translator import Translator


@dataclass
class RegisterPrivateConsumptionController:
    @dataclass
    class FormError(Exception):
        form: RegisterPrivateConsumptionForm

    translator: Translator

    def import_form_data(
        self, current_user: UUID, request: Request
    ) -> RegisterPrivateConsumptionRequest:
        plan_id: UUID
        amount: int
        if plan_id_field := request.get_form("plan_id"):
            try:
                plan_id = UUID(plan_id_field)
            except ValueError:
                raise self.create_form_error(
                    request,
                    plan_id_errors=[self.translator.gettext("Plan ID is invalid.")],
                )
        else:
            raise self.create_form_error(
                request, plan_id_errors=[self.translator.gettext("Plan ID is invalid.")]
            )
        if amount_field := request.get_form("amount"):
            try:
                amount = int(amount_field)
            except ValueError:
                raise self.create_form_error(
                    request,
                    amount_errors=[self.translator.gettext("This is not an integer.")],
                )
        else:
            raise self.create_form_error(
                request,
                amount_errors=[self.translator.gettext("You must specify an amount.")],
            )
        if amount < 1:
            raise self.create_form_error(
                request,
                amount_errors=[
                    self.translator.gettext("Must be a number larger than zero.")
                ],
            )
        return RegisterPrivateConsumptionRequest(
            consumer=current_user, plan=plan_id, amount=amount
        )

    def create_form_error(
        self,
        request: Request,
        *,
        plan_id_errors: list[str] | None = None,
        amount_errors: list[str] | None = None,
    ) -> FormError:
        if plan_id_errors is None:
            plan_id_errors = []
        if amount_errors is None:
            amount_errors = []
        return self.FormError(
            form=RegisterPrivateConsumptionForm(
                plan_id_value=request.get_form("plan_id") or "",
                plan_id_errors=plan_id_errors,
                amount_value=request.get_form("amount") or "",
                amount_errors=amount_errors,
            )
        )
