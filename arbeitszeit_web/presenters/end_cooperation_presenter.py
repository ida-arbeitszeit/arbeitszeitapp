from dataclasses import dataclass
from urllib.parse import urlparse
from uuid import UUID

from arbeitszeit.use_cases.end_cooperation import EndCooperationResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import CoopSummaryUrlIndex, PlanSummaryUrlIndex


@dataclass
class EndCooperationPresenter:
    @dataclass
    class ViewModel:
        show_404: bool
        redirect_url: str

    request: Request
    notifier: Notifier
    plan_summary_index: PlanSummaryUrlIndex
    coop_summary_index: CoopSummaryUrlIndex
    translator: Translator

    def present(self, response: EndCooperationResponse) -> ViewModel:
        if response.is_rejected:
            self.notifier.display_warning(
                self.translator.gettext("Cooperation could not be terminated.")
            )
            return self.ViewModel(show_404=True, redirect_url="")
        self.notifier.display_info(
            self.translator.gettext("Cooperation has been terminated.")
        )
        redirect_url = self._get_redirect_url()
        return self.ViewModel(show_404=False, redirect_url=redirect_url)

    def _get_redirect_url(self) -> str:
        referer = self.request.get_header("HTTP_REFERER")
        query_string = self.request.query_string()
        plan_id = query_string.get("plan_id")
        cooperation_id = query_string.get("cooperation_id")
        assert plan_id
        assert cooperation_id
        if referer:
            if self._refers_from_plan_summary(referer):
                url = self.plan_summary_index.get_plan_summary_url(UUID(plan_id))
                return url
        url = self.coop_summary_index.get_coop_summary_url(UUID(cooperation_id))
        return url

    def _refers_from_plan_summary(self, referer: str) -> bool:
        referer_path = urlparse(referer).path
        return True if referer_path.startswith("/company/plan_summary") else False
