from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumptionRequest,
)
from arbeitszeit_web.fields import parse_formfield
from arbeitszeit_web.forms import RegisterPrivateConsumptionForm
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.www.formfield_parsers import PositiveIntegerParser, UuidParser


@dataclass
class RegisterPrivateConsumptionController:
    class FormError(Exception):
        pass

    positive_integer_parser: PositiveIntegerParser
    uuid_parser: UuidParser
    translator: Translator

    def import_form_data(
        self, current_user: UUID, form: RegisterPrivateConsumptionForm
    ) -> RegisterPrivateConsumptionRequest:
        plan_id = parse_formfield(
            form.plan_id_field(),
            self.uuid_parser.with_invalid_uuid_message(
                self.translator.gettext("Plan ID is invalid.")
            ),
        )
        amount = parse_formfield(
            form.amount_field(),
            self.positive_integer_parser,
        )
        if not plan_id or not amount:
            raise self.FormError()
        return RegisterPrivateConsumptionRequest(
            consumer=current_user, plan=plan_id.value, amount=amount.value
        )
