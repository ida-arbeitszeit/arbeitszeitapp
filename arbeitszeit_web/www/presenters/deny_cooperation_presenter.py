from dataclasses import dataclass

from arbeitszeit.use_cases.deny_cooperation import DenyCooperationResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirection_url: str


@dataclass
class DenyCooperationPresenter:
    translator: Translator
    notifier: Notifier
    url_index: UrlIndex

    def render_response(
        self, deny_cooperation_response: DenyCooperationResponse
    ) -> ViewModel:
        if not deny_cooperation_response.is_rejected:
            self.notifier.display_info(
                self.translator.gettext("Cooperation request has been denied.")
            )
        else:
            if (
                deny_cooperation_response
                == DenyCooperationResponse.RejectionReason.plan_not_found
                or DenyCooperationResponse.RejectionReason.cooperation_not_found
            ):
                self.notifier.display_warning(
                    self.translator.gettext("Plan or cooperation not found.")
                )
            elif (
                deny_cooperation_response
                == DenyCooperationResponse.RejectionReason.cooperation_was_not_requested
            ):
                self.notifier.display_warning(
                    self.translator.gettext("This cooperation request does not exist.")
                )
            elif (
                deny_cooperation_response
                == DenyCooperationResponse.RejectionReason.requester_is_not_coordinator
            ):
                self.notifier.display_warning(
                    self.translator.gettext(
                        "You are not coordinator of this cooperation."
                    )
                )
            else:
                # catchall for rejected responses where rejection
                # reason cannot be handled by presenter.
                self.notifier.display_warning(
                    self.translator.gettext("Could not deny cooperation")
                )
        return ViewModel(redirection_url=self.url_index.get_my_cooperations_url())
