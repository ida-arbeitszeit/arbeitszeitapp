from dataclasses import dataclass

from arbeitszeit.use_cases.edit_draft import Response
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirect_url: str | None


@dataclass
class EditDraftPresenter:
    url_index: UrlIndex

    def render_response(self, response: Response) -> ViewModel:
        if response.is_success:
            return ViewModel(redirect_url=self.url_index.get_my_plans_url())
        else:
            return ViewModel(redirect_url=None)
