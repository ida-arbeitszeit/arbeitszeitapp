from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.use_cases.create_plan_draft import Response
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class CreateDraftPresenter:
    @dataclass
    class ViewModel:
        redirect_url: str | None

    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def present_plan_creation(self, response: Response) -> ViewModel:
        if response.draft_id is None:
            return self.ViewModel(redirect_url=None)
        else:
            self.notifier.display_info(
                self.translator.gettext("Plan draft successfully created")
            )
            return self.ViewModel(redirect_url=self.url_index.get_my_plan_drafts_url())
