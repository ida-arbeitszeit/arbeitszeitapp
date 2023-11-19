from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import create_draft_from_plan as use_case
from arbeitszeit_web.session import Session, UserRole


@dataclass
class CreateDraftFromPlanController:
    session: Session

    def create_use_case_request(self, plan: UUID) -> use_case.Request:
        assert self.session.get_user_role() == UserRole.company
        user = self.session.get_current_user()
        assert user
        return use_case.Request(
            plan=plan,
            company=user,
        )
