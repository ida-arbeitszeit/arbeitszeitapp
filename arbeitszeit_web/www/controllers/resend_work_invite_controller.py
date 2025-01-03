from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import resend_work_invite
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session, UserRole


@dataclass
class ResendWorkInviteController:
    session: Session

    def create_use_case_request(self, request: Request) -> resend_work_invite.Request:
        user_role = self.session.get_user_role()
        assert user_role == UserRole.company
        company_id = self.session.get_current_user()
        assert company_id
        worker_id = self._get_worker_id(request)
        return resend_work_invite.Request(
            company=company_id,
            worker=worker_id,
        )

    def _get_worker_id(self, request: Request) -> UUID:
        worker_id = request.get_form("worker_id") or ""
        worker_id = worker_id.strip()
        return UUID(worker_id)
