from typing import Optional, Protocol
from uuid import UUID

from arbeitszeit.use_cases import InviteWorkerToCompanyRequest


class InviteWorkerToCompanyForm(Protocol):
    def get_worker_id(self) -> str:
        ...


class InviteWorkerToCompanyController:
    def import_request_data(
        self, current_user: Optional[UUID], form: InviteWorkerToCompanyForm
    ) -> InviteWorkerToCompanyRequest:
        if current_user is None:
            raise ValueError("User is not logged in")
        try:
            worker_uuid = UUID(form.get_worker_id())
        except ValueError:
            raise ValueError("worker_id is not a valid UUID")
        return InviteWorkerToCompanyRequest(
            company=current_user,
            worker=worker_uuid,
        )
