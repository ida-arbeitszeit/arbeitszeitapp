from dataclasses import dataclass

from arbeitszeit.interactors import create_draft_from_plan as interactor
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirect_url: str


@dataclass
class CreateDraftFromPlanPresenter:
    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def render_response(
        self,
        interactor_response: interactor.Response,
        request: Request,
    ) -> ViewModel:
        self.notifier.display_info(
            self.translator.gettext("A new draft was created from an expired plan.")
        )
        if interactor_response.draft:
            return ViewModel(
                redirect_url=self.url_index.get_draft_details_url(
                    interactor_response.draft
                )
            )
        else:
            return ViewModel(
                redirect_url=request.get_header("Referer")
                or self.url_index.get_my_plans_url()
            )
