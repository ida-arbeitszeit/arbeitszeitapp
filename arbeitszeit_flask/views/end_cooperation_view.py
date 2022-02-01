from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
from uuid import UUID

from flask import Response, redirect

from arbeitszeit.use_cases.end_cooperation import EndCooperation, EndCooperationRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.views.http_404_view import Http404View
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.url_index import CoopSummaryUrlIndex, PlanSummaryUrlIndex


@dataclass
class EndCooperationView:
    notifier: Notifier
    session: FlaskSession
    end_cooperation: EndCooperation
    http_404_view: Http404View
    plan_summary_index: PlanSummaryUrlIndex
    coop_summary_index: CoopSummaryUrlIndex

    def respond_to_get(self, request) -> Response:
        plan_id = request.args.get("plan_id", None)
        cooperation_id = request.args.get("cooperation_id", None)
        current_user = self.session.get_current_user()
        assert plan_id
        assert cooperation_id
        assert current_user
        use_case_request = EndCooperationRequest(
            current_user, UUID(plan_id), UUID(cooperation_id)
        )
        response = self.end_cooperation(use_case_request)
        if response.is_rejected:
            return self.http_404_view.get_response()
        self.notifier.display_info("Kooperation wurde erfolgreich beendet.")
        referer = self._get_referer(request)
        if referer:
            if self._refers_from_plan_summary(referer):
                url = self.plan_summary_index.get_plan_summary_url(UUID(plan_id))
                return redirect(url)
        url = self.coop_summary_index.get_coop_summary_url(UUID(cooperation_id))
        return redirect(url)

    def _get_referer(self, request) -> Optional[str]:
        referer = request.environ.get("HTTP_REFERER", None)
        return referer

    def _refers_from_plan_summary(self, referer: str) -> bool:
        referer_path = urlparse(referer).path
        return True if referer_path.startswith("/company/plan_summary") else False
