from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.use_cases.end_cooperation import EndCooperationRequest
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session


@dataclass
class EndCooperationController:
    session: Session
    request: Request

    def process_request_data(self) -> Optional[EndCooperationRequest]:
        plan_id = self.request.get_form("plan_id")
        cooperation_id = self.request.get_form("cooperation_id")
        current_user = self.session.get_current_user()
        if not all([plan_id, cooperation_id, current_user]):
            return None
        assert plan_id
        assert cooperation_id
        assert current_user

        try:
            plan_uuid = UUID(plan_id)
            cooperation_uuid = UUID(cooperation_id)
        except ValueError:
            return None

        use_case_request = EndCooperationRequest(
            current_user, plan_uuid, cooperation_uuid
        )
        return use_case_request
