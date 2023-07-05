from dataclasses import dataclass

from arbeitszeit.use_cases.list_workers import ListWorkersRequest
from arbeitszeit_web.session import Session


@dataclass
class ListWorkersController:
    session: Session

    def create_use_case_request(self) -> ListWorkersRequest:
        current_user = self.session.get_current_user()
        assert current_user
        return ListWorkersRequest(company=current_user)
