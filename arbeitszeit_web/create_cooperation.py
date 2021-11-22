from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases import CreateCooperationResponse


@dataclass
class CreateCooperationViewModel:
    notifications: List[str]


class CreateCooperationPresenter:
    def present(
        self, use_case_response: CreateCooperationResponse
    ) -> CreateCooperationViewModel:
        notifications = []
        if not use_case_response.is_rejected:
            notifications.append("Kooperation erfolgreich erstellt.")
        elif (
            use_case_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
        ):
            notifications.append(
                "Es existiert bereits eine Kooperation mit diesem Namen."
            )
        elif (
            use_case_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.coordinator_not_found
        ):
            notifications.append("Interner Fehler: Koordinator nicht gefunden.")
        return CreateCooperationViewModel(notifications)
