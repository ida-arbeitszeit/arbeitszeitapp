from dataclasses import dataclass
from typing import assert_never
from uuid import UUID

from arbeitszeit.interactors.request_coordination_transfer import (
    RequestCoordinationTransferInteractor as Interactor,
)
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem


@dataclass
class RequestCoordinationTransferViewModel:
    status_code: int


@dataclass
class RequestCoordinationTransferPresenter:
    translator: Translator
    notifier: Notifier
    url_index: UrlIndex

    def create_navbar_items(self, coop_id: UUID) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("Cooperation"),
                url=self.url_index.get_coop_summary_url(
                    coop_id=coop_id,
                ),
            ),
            NavbarItem(
                text=self.translator.gettext("Request Coordination Transfer"),
                url=None,
            ),
        ]

    def present_interactor_response(
        self, interactor_response: Interactor.Response
    ) -> RequestCoordinationTransferViewModel:
        if interactor_response.is_rejected:
            assert interactor_response.rejection_reason
            if (
                interactor_response.rejection_reason
                == Interactor.Response.RejectionReason.candidate_is_not_a_company
            ):
                self.notifier.display_warning(
                    self.translator.gettext("The candidate is not a company.")
                )
                return RequestCoordinationTransferViewModel(status_code=404)
            elif (
                interactor_response.rejection_reason
                == Interactor.Response.RejectionReason.requester_is_not_coordinator
            ):
                self.notifier.display_warning(
                    self.translator.gettext("You are not the coordinator.")
                )
                return RequestCoordinationTransferViewModel(status_code=403)
            elif (
                interactor_response.rejection_reason
                == Interactor.Response.RejectionReason.candidate_is_current_coordinator
            ):
                self.notifier.display_warning(
                    self.translator.gettext("The candidate is already the coordinator.")
                )
                return RequestCoordinationTransferViewModel(status_code=409)
            elif (
                interactor_response.rejection_reason
                == Interactor.Response.RejectionReason.coordination_tenure_has_pending_transfer_request
            ):
                self.notifier.display_warning(
                    self.translator.gettext(
                        "Request has not been sent. You have a pending transfer request."
                    )
                )
                return RequestCoordinationTransferViewModel(status_code=409)
            elif (
                interactor_response.rejection_reason
                == Interactor.Response.RejectionReason.cooperation_not_found
            ):
                self.notifier.display_warning(
                    self.translator.gettext("Cooperation not found.")
                )
                return RequestCoordinationTransferViewModel(status_code=404)
            assert_never(interactor_response.rejection_reason)
        else:
            self.notifier.display_info(
                self.translator.gettext("Request has been sent.")
            )
            return RequestCoordinationTransferViewModel(status_code=200)
