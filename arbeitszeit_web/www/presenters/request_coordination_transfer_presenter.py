from dataclasses import dataclass

from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase as UseCase,
)
from arbeitszeit_web.translator import Translator


@dataclass
class RequestCoordinationTransferViewModel:
    notifications: list[str]
    is_error: bool


@dataclass
class RequestCoordinationTransferPresenter:
    translator: Translator

    def present(
        self, use_case_response: UseCase.Response
    ) -> RequestCoordinationTransferViewModel:
        notifications = []
        if not use_case_response.is_rejected:
            is_error = False
            notifications.append(self.translator.gettext("Request has been sent."))
        else:
            is_error = True
            if (
                use_case_response.rejection_reason
                == UseCase.Response.RejectionReason.candidate_is_not_a_company
            ):
                notifications.append(
                    self.translator.gettext("The candidate is not a company.")
                )
            elif (
                use_case_response.rejection_reason
                == UseCase.Response.RejectionReason.requesting_tenure_not_found
            ):
                notifications.append(
                    self.translator.gettext("Requesting coordination tenure not found.")
                )
            elif (
                use_case_response.rejection_reason
                == UseCase.Response.RejectionReason.candidate_is_current_coordinator
            ):
                notifications.append(
                    self.translator.gettext("The candidate is already the coordinator.")
                )
            elif (
                use_case_response.rejection_reason
                == UseCase.Response.RejectionReason.requesting_tenure_is_not_current_tenure
            ):
                notifications.append(
                    self.translator.gettext(
                        "The requesting coordination tenure is not the current tenure."
                    )
                )
            elif (
                use_case_response.rejection_reason
                == UseCase.Response.RejectionReason.requesting_tenure_has_pending_transfer_request
            ):
                notifications.append(
                    self.translator.gettext(
                        "The requesting coordination tenure has a pending transfer request."
                    )
                )
        return RequestCoordinationTransferViewModel(notifications, is_error)
