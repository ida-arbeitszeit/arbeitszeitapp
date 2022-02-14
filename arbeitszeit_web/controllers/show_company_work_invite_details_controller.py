from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.use_cases import ShowCompanyWorkInviteDetailsRequest

from ..session import Session


@dataclass
class ShowCompanyWorkInviteDetailsController:
    session: Session

    def create_use_case_request(
        self, invite_id: UUID
    ) -> Optional[ShowCompanyWorkInviteDetailsRequest]:
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        return ShowCompanyWorkInviteDetailsRequest(
            invite=invite_id,
            member=current_user,
        )
