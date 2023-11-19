from dataclasses import dataclass

from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase as UseCase,
)
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator

ERROR_MESSAGES = {
    UseCase.Response.RejectionReason.candidate_is_not_a_company: "The candidate is not a company.",
    UseCase.Response.RejectionReason.requesting_tenure_not_found: "Requesting coordination tenure not found.",
    UseCase.Response.RejectionReason.candidate_is_current_coordinator: "The candidate is already the coordinator.",
    UseCase.Response.RejectionReason.requesting_tenure_is_not_current_tenure: "The requesting coordination tenure is not the current tenure.",
    UseCase.Response.RejectionReason.requesting_tenure_has_pending_transfer_request: "The requesting coordination tenure has a pending transfer request.",
}


@dataclass
class RequestCoordinationTransferPresenter:
    translator: Translator
    notifier: Notifier

    def present(self, use_case_response: UseCase.Response) -> None:
        if use_case_response.is_rejected:
            assert use_case_response.rejection_reason
            if message := ERROR_MESSAGES.get(use_case_response.rejection_reason):
                self.notifier.display_warning(self.translator.gettext(message))
            else:
                self.notifier.display_warning(
                    self.translator.gettext(
                        "Unknown error ocurred. Request has not been sent."
                    )
                )
        else:
            self.notifier.display_info(
                self.translator.gettext("Request has been sent.")
            )
