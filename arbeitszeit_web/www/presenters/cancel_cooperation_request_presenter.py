from dataclasses import dataclass

from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirection_url: str


@dataclass
class CancelCooperationRequestPresenter:
    translator: Translator
    notifier: Notifier
    url_index: UrlIndex

    def render_response(self, response: bool) -> ViewModel:
        if response:
            self.notifier.display_info(
                self.translator.gettext("Cooperation request has been canceled.")
            )
        else:
            self.notifier.display_warning(
                self.translator.gettext("Error: Not possible to cancel request.")
            )
        return ViewModel(redirection_url=self.url_index.get_my_cooperations_url())
