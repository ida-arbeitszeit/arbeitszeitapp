from dataclasses import dataclass
from typing import List, Protocol, Union
from uuid import UUID

from arbeitszeit.use_cases import RequestCooperationRequest, RequestCooperationResponse

from .malformed_input_data import MalformedInputData
from .session import Session


@dataclass
class RequestCooperationViewModel:
    notifications: List[str]
    is_error: bool


class RequestCooperationPresenter:
    def present(
        self, use_case_response: RequestCooperationResponse
    ) -> RequestCooperationViewModel:
        view_model = self._create_view_model(use_case_response)
        return view_model

    def _create_view_model(
        self, use_case_response: RequestCooperationResponse
    ) -> RequestCooperationViewModel:
        notifications = []
        if not use_case_response.is_rejected:
            is_error = False
            notifications.append("Anfrage wurde gestellt.")
        else:
            is_error = True
            if (
                use_case_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.plan_not_found
            ):
                notifications.append("Plan nicht gefunden.")
            elif (
                use_case_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.cooperation_not_found
            ):
                notifications.append("Kooperation nicht gefunden.")
            elif (
                use_case_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.plan_inactive
            ):
                notifications.append("Plan nicht aktiv.")
            elif use_case_response.rejection_reason in (
                RequestCooperationResponse.RejectionReason.plan_has_cooperation,
                RequestCooperationResponse.RejectionReason.plan_is_already_requesting_cooperation,
            ):
                notifications.append(
                    "Plan kooperiert bereits oder hat Kooperation angefragt."
                )
            elif (
                use_case_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.plan_is_public_service
            ):
                notifications.append("Öffentliche Pläne können nicht kooperieren.")
            elif (
                use_case_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.requester_is_not_planner
            ):
                notifications.append(
                    "Nur der Ersteller des Plans kann Kooperation anfragen."
                )
        return RequestCooperationViewModel(
            notifications=notifications, is_error=is_error
        )


class RequestCooperationForm(Protocol):
    def get_plan_id_string(self) -> str:
        ...

    def get_cooperation_id_string(self) -> str:
        ...


@dataclass
class RequestCooperationController:
    session: Session

    def import_form_data(
        self, form: RequestCooperationForm
    ) -> Union[RequestCooperationRequest, MalformedInputData, None]:
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        try:
            plan_uuid = UUID(form.get_plan_id_string())
        except (ValueError, TypeError):
            return MalformedInputData("plan_id", "Plan-ID ist ungültig.")
        try:
            cooperation_uuid = UUID(form.get_cooperation_id_string())
        except ValueError:
            return MalformedInputData("cooperation_id", "Kooperations-ID ist ungültig.")
        return RequestCooperationRequest(
            requester_id=current_user,
            plan_id=plan_uuid,
            cooperation_id=cooperation_uuid,
        )
