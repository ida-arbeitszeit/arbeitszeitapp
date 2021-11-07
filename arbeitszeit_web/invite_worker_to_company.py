from dataclasses import dataclass
from typing import List, Optional, Protocol
from uuid import UUID

from arbeitszeit.use_cases import (
    InviteWorkerToCompanyRequest,
    InviteWorkerToCompanyResponse,
)


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


@dataclass
class ViewModel:
    notifications: List[str]


class InviteWorkerToCompanyPresenter:
    def present(self, use_case_response: InviteWorkerToCompanyResponse) -> ViewModel:
        if use_case_response.is_success:
            notifications = ["Arbeiter*in erfolgreich eingeladen."]
        else:
            notifications = ["Arbeiter*in konnte nicht eingeladen werden."]
        return ViewModel(
            notifications=notifications,
        )
