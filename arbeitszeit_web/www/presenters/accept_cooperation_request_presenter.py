from dataclasses import dataclass

from arbeitszeit.use_cases.accept_cooperation import AcceptCooperationResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModel:
    redirection_url: str


@dataclass
class AcceptCooperationRequestPresenter:
    translator: Translator
    notifier: Notifier

    def render_response(self, response: AcceptCooperationResponse) -> ViewModel:
        if not response.is_rejected:
            self.notifier.display_info(
                self.translator.gettext("Cooperation request has been accepted.")
            )
        else:
            if (
                response == AcceptCooperationResponse.RejectionReason.plan_not_found
                or AcceptCooperationResponse.RejectionReason.cooperation_not_found
            ):
                self.notifier.display_warning(
                    self.translator.gettext("Plan or cooperation not found.")
                )
            elif (
                response == AcceptCooperationResponse.RejectionReason.plan_inactive
                or AcceptCooperationResponse.RejectionReason.plan_has_cooperation
                or AcceptCooperationResponse.RejectionReason.plan_is_public_service
            ):
                self.notifier.display_warning(
                    self.translator.gettext("Something's wrong with that plan.")
                )
            elif (
                response
                == AcceptCooperationResponse.RejectionReason.cooperation_was_not_requested
            ):
                self.notifier.display_warning(
                    self.translator.gettext("This cooperation request does not exist.")
                )
            elif (
                response
                == AcceptCooperationResponse.RejectionReason.requester_is_not_coordinator
            ):
                self.notifier.display_warning(
                    self.translator.gettext(
                        "You are not coordinator of this cooperation."
                    )
                )
        return ViewModel(redirection_url="/company/my_cooperations")
