from dataclasses import dataclass

from arbeitszeit.use_cases import create_draft_from_plan as use_case
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
    request: Request
    notifier: Notifier
    translator: Translator

    def render_response(self, response: use_case.Response) -> ViewModel:
        self.notifier.display_info(
            self.translator.gettext("A new draft was created from an expired plan.")
        )
        if response.draft:
            return ViewModel(
                redirect_url=self.url_index.get_draft_details_url(response.draft)
            )
        else:
            return ViewModel(
                redirect_url=self.request.get_header("Referer")
                or self.url_index.get_my_plans_url()
            )
