from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase as UseCase,
)
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem

ERROR_MESSAGES = {
    UseCase.Response.RejectionReason.candidate_is_not_a_company: "The candidate is not a company.",
    UseCase.Response.RejectionReason.requester_is_not_coordinator: "You are not the coordinator.",
    UseCase.Response.RejectionReason.cooperation_not_found: "Cooperation not found.",
    UseCase.Response.RejectionReason.candidate_is_current_coordinator: "The candidate is already the coordinator.",
    UseCase.Response.RejectionReason.coordination_tenure_has_pending_transfer_request: "The requesting coordination tenure has a pending transfer request.",
}


@dataclass
class RequestCoordinationTransferPresenter:
    translator: Translator
    notifier: Notifier
    url_index: UrlIndex
    session: Session

    def create_navbar_items(self, coop_id: UUID) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("Cooperation"),
                url=self.url_index.get_coop_summary_url(
                    coop_id=coop_id,
                    user_role=self.session.get_user_role(),
                ),
            ),
            NavbarItem(
                text=self.translator.gettext("Request Coordination Transfer"),
                url=None,
            ),
        ]

    def present_use_case_response(self, use_case_response: UseCase.Response) -> None:
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
