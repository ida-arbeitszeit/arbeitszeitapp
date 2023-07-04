from dataclasses import dataclass
from typing import Protocol, Union
from uuid import UUID

from arbeitszeit.use_cases.request_cooperation import RequestCooperationRequest
from arbeitszeit_web.malformed_input_data import MalformedInputData
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator


class RequestCooperationForm(Protocol):
    def get_plan_id_string(self) -> str:
        ...

    def get_cooperation_id_string(self) -> str:
        ...


@dataclass
class RequestCooperationController:
    session: Session
    translator: Translator

    def import_form_data(
        self, form: RequestCooperationForm
    ) -> Union[RequestCooperationRequest, MalformedInputData, None]:
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        try:
            plan_uuid = UUID(form.get_plan_id_string())
        except (ValueError, TypeError):
            return MalformedInputData(
                "plan_id", self.translator.gettext("Invalid plan ID.")
            )
        try:
            cooperation_uuid = UUID(form.get_cooperation_id_string())
        except ValueError:
            return MalformedInputData(
                "cooperation_id",
                self.translator.gettext("Invalid cooperation ID."),
            )
        return RequestCooperationRequest(
            requester_id=current_user,
            plan_id=plan_uuid,
            cooperation_id=cooperation_uuid,
        )
