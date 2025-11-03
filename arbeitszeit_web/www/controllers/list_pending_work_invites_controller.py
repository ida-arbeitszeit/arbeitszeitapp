from dataclasses import dataclass

from arbeitszeit.interactors import list_pending_work_invites
from arbeitszeit_web.session import Session, UserRole


@dataclass
class ListPendingWorkInvitesController:
    session: Session

    def create_interactor_request(self) -> list_pending_work_invites.Request:
        current_user_role = self.session.get_user_role()
        assert current_user_role == UserRole.company
        current_company = self.session.get_current_user()
        assert current_company
        return list_pending_work_invites.Request(company=current_company)
