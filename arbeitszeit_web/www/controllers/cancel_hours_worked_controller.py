from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import cancel_hours_worked
from arbeitszeit_web.session import Session, UserRole


@dataclass
class CancelHoursWorkedController:
    session: Session

    def create_use_case_request(
        self, registration_id: UUID
    ) -> cancel_hours_worked.Request:
        assert self.session.get_user_role() == UserRole.company
        user = self.session.get_current_user()
        assert user
        return cancel_hours_worked.Request(
            requester=user,
            registration_id=registration_id,
        )
