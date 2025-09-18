from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.interactors.register_productive_consumption import (
    RegisterProductiveConsumptionRequest,
)
from arbeitszeit.records import ConsumptionType
from arbeitszeit_web.forms import RegisterProductiveConsumptionForm
from arbeitszeit_web.forms.fields import ParsingFailure, ParsingSuccess, parse_formfield
from arbeitszeit_web.forms.formfield_parsers import PositiveIntegerParser, UuidParser
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator


@dataclass
class RegisterProductiveConsumptionController:
    class FormError(Exception):
        pass

    session: Session
    uuid_parser: UuidParser
    positive_integer_parser: PositiveIntegerParser
    type_of_consumption_parser: TypeOfConsumptionParser
    translator: Translator

    def process_input_data(
        self, form: RegisterProductiveConsumptionForm
    ) -> RegisterProductiveConsumptionRequest:
        consumer = self.session.get_current_user()
        assert consumer
        plan = parse_formfield(
            form.plan_id_field(),
            self.uuid_parser.with_invalid_uuid_message(
                self.translator.gettext("Invalid ID.")
            ),
        )
        amount = parse_formfield(form.amount_field(), self.positive_integer_parser)
        type_of_consumption = parse_formfield(
            form.type_of_consumption_field(), self.type_of_consumption_parser
        )
        if not (plan and amount and type_of_consumption):
            raise self.FormError()
        return RegisterProductiveConsumptionRequest(
            consumer, plan.value, amount.value, type_of_consumption.value
        )


@dataclass
class TypeOfConsumptionParser:
    translator: Translator

    def __call__(
        self, candidate: str
    ) -> ParsingSuccess[ConsumptionType] | ParsingFailure:
        if not candidate:
            return ParsingFailure([self.translator.gettext("This field is required.")])
        return ParsingSuccess(
            ConsumptionType.means_of_prod
            if candidate == "fixed"
            else ConsumptionType.raw_materials
        )
