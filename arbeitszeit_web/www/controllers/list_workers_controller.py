from dataclasses import dataclass

from arbeitszeit.use_cases import list_workers
from arbeitszeit_web.session import Session


@dataclass
class ListWorkersController:
    session: Session

    def create_use_case_request(self) -> list_workers.Request:
        current_user = self.session.get_current_user()
        assert current_user
        return list_workers.Request(company=current_user)
