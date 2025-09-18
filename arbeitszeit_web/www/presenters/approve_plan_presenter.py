from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.interactors.approve_plan import ApprovePlanInteractor as Interactor
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ApprovePlanPresenter:
    @dataclass
    class ViewModel:
        redirect_url: str

    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def approve_plan(self, response: Interactor.Response) -> ViewModel:
        if response.is_plan_approved:
            self.notifier.display_info(
                self.translator.gettext("Plan was approved successfully")
            )
        else:
            self.notifier.display_warning(
                self.translator.gettext("Plan approval failed")
            )
        return self.ViewModel(
            redirect_url=self.url_index.get_unreviewed_plans_list_view_url()
        )
