from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.interactors.show_company_work_invite_details import (
    ShowCompanyWorkInviteDetailsRequest,
)

from ...session import Session


@dataclass
class ShowCompanyWorkInviteDetailsController:
    session: Session

    def create_interactor_request(
        self, invite_id: UUID
    ) -> Optional[ShowCompanyWorkInviteDetailsRequest]:
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        return ShowCompanyWorkInviteDetailsRequest(
            invite=invite_id,
            member=current_user,
        )
