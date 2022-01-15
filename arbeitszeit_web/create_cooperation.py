from dataclasses import dataclass

from injector import inject

from arbeitszeit.use_cases import CreateCooperationResponse

from .notification import Notifier


@dataclass
class CreateCooperationViewModel:
    pass


@inject
@dataclass(frozen=True)
class CreateCooperationPresenter:
    user_notifier: Notifier

    def present(
        self, use_case_response: CreateCooperationResponse
    ) -> CreateCooperationViewModel:
        if not use_case_response.is_rejected:
            self.user_notifier.display_info("Kooperation erfolgreich erstellt.")
        elif (
            use_case_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
        ):
            self.user_notifier.display_warning(
                "Es existiert bereits eine Kooperation mit diesem Namen."
            )
        elif (
            use_case_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.coordinator_not_found
        ):
            self.user_notifier.display_warning(
                "Interner Fehler: Koordinator nicht gefunden."
            )
        return CreateCooperationViewModel()
