from dataclasses import dataclass

from arbeitszeit.interactors import list_registered_hours_worked
from arbeitszeit_web.session import Session, UserRole


@dataclass
class ListRegisteredHoursWorkedController:
    session: Session

    def create_request(self) -> list_registered_hours_worked.Request:
        current_user_role = self.session.get_user_role()
        assert current_user_role == UserRole.company
        current_company = self.session.get_current_user()
        assert current_company
        return list_registered_hours_worked.Request(company_id=current_company)
