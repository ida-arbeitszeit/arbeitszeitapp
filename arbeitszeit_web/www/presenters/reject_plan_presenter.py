from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.interactors.reject_plan import RejectPlanInteractor as Interactor
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class RejectPlanPresenter:
    @dataclass
    class ViewModel:
        redirect_url: str

    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def reject_plan(self, response: Interactor.Response) -> ViewModel:
        if response.is_plan_rejected:
            self.notifier.display_info(
                self.translator.gettext(
                    "Plan was rejected successfully. An email was sent to the planning company."
                )
            )
        else:
            self.notifier.display_warning(
                self.translator.gettext("Plan rejection failed. No email sent.")
            )
        return self.ViewModel(
            redirect_url=self.url_index.get_unreviewed_plans_list_view_url()
        )
