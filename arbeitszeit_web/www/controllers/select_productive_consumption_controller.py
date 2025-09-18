from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.interactors.select_productive_consumption import (
    Request as InteractorRequest,
)
from arbeitszeit.records import ConsumptionType
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.translator import Translator


@dataclass
class SelectProductiveConsumptionController:
    class InputDataError(Exception):
        pass

    notifier: Notifier
    translator: Translator

    def process_input_data(self, request: Request) -> InteractorRequest:
        plan_id = self._process_plan_id(request)
        amount = self._process_amount(request)
        consumption_type = self._process_consumption_type(request)
        return InteractorRequest(
            plan_id=plan_id, amount=amount, consumption_type=consumption_type
        )

    def _process_plan_id(self, request: Request) -> UUID | None:
        plan_id_from_query_string = request.query_string().get_last_value("plan_id")
        plan_id_from_form = request.get_form("plan_id")
        if not plan_id_from_query_string and not plan_id_from_form:
            return None
        elif plan_id_from_query_string:
            return self._convert_string_to_uuid(plan_id_from_query_string)
        else:
            assert plan_id_from_form
            return self._convert_string_to_uuid(plan_id_from_form)

    def _convert_string_to_uuid(self, input_string: str) -> UUID:
        try:
            return UUID(input_string)
        except ValueError:
            self.notifier.display_warning(
                self.translator.gettext("The provided plan ID is not a valid UUID.")
            )
            raise self.InputDataError()

    def _process_amount(self, request: Request) -> int | None:
        amount_from_query_string = request.query_string().get_last_value("amount")
        amount_from_form = request.get_form("amount")
        if not amount_from_query_string and not amount_from_form:
            return None
        elif amount_from_query_string:
            return self._convert_string_to_int(amount_from_query_string)
        else:
            assert amount_from_form
            return self._convert_string_to_int(amount_from_form)

    def _convert_string_to_int(self, input_string: str) -> int:
        try:
            return int(input_string)
        except ValueError:
            self.notifier.display_warning(
                self.translator.gettext("The provided amount is not a valid integer.")
            )
            raise self.InputDataError()

    def _process_consumption_type(self, request: Request) -> ConsumptionType | None:
        consumption_type_from_query_string = request.query_string().get_last_value(
            "type_of_consumption"
        )
        consumption_type_from_form = request.get_form("type_of_consumption")
        if not consumption_type_from_query_string and not consumption_type_from_form:
            return None
        elif consumption_type_from_query_string:
            return self._convert_string_to_consumption_type(
                consumption_type_from_query_string
            )
        else:
            assert consumption_type_from_form
            return self._convert_string_to_consumption_type(consumption_type_from_form)

    def _convert_string_to_consumption_type(self, input_string: str) -> ConsumptionType:
        if input_string == "fixed":
            return ConsumptionType.means_of_prod
        elif input_string == "liquid":
            return ConsumptionType.raw_materials
        else:
            self.notifier.display_warning(
                self.translator.gettext(
                    "The provided type of consumption is not valid."
                )
            )
            raise self.InputDataError()
