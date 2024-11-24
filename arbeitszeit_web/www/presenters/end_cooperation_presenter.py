from dataclasses import dataclass
from urllib.parse import urlparse
from uuid import UUID

from arbeitszeit.use_cases.end_cooperation import EndCooperationResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class EndCooperationPresenter:
    @dataclass
    class ViewModel:
        show_404: bool
        redirect_url: str

    notifier: Notifier
    url_index: UrlIndex
    translator: Translator
    session: Session

    def present(
        self, response: EndCooperationResponse, *, web_request: Request
    ) -> ViewModel:
        if response.is_rejected:
            self.notifier.display_warning(
                self.translator.gettext("Cooperation could not be terminated.")
            )
            return self.ViewModel(show_404=True, redirect_url="")
        self.notifier.display_info(
            self.translator.gettext("Cooperation has been terminated.")
        )
        redirect_url = self._get_redirect_url(web_request)
        return self.ViewModel(show_404=False, redirect_url=redirect_url)

    def _get_redirect_url(self, request: Request) -> str:
        referer = request.get_header("Referer")
        query_string = request.query_string()
        plan_id = query_string.get_last_value("plan_id") or request.get_form("plan_id")
        cooperation_id = query_string.get_last_value(
            "cooperation_id"
        ) or request.get_form("cooperation_id")
        assert plan_id
        assert cooperation_id
        if referer:
            if self._refers_from_plan_details(referer):
                url = self.url_index.get_plan_details_url(
                    user_role=self.session.get_user_role(), plan_id=UUID(plan_id)
                )
                return url
        url = self.url_index.get_coop_summary_url(coop_id=UUID(cooperation_id))
        return url

    def _refers_from_plan_details(self, referer: str) -> bool:
        referer_path = urlparse(referer).path
        return True if referer_path.startswith("/company/plan_details") else False
