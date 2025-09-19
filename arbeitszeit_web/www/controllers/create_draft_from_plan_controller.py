from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.interactors import create_draft_from_plan as interactor
from arbeitszeit_web.session import Session, UserRole


@dataclass
class CreateDraftFromPlanController:
    session: Session

    def create_interactor_request(self, plan: UUID) -> interactor.Request:
        assert self.session.get_user_role() == UserRole.company
        user = self.session.get_current_user()
        assert user
        return interactor.Request(
            plan=plan,
            company=user,
        )
