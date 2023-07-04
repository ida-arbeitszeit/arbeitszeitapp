from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from arbeitszeit_web.session import Session


class InviteWorkerToCompanyForm(Protocol):
    def get_worker_id(self) -> str:
        ...


@dataclass
class InviteWorkerToCompanyController:
    session: Session

    def import_request_data(
        self, form: InviteWorkerToCompanyForm
    ) -> InviteWorkerToCompanyUseCase.Request:
        return InviteWorkerToCompanyUseCase.Request(
            company=self._get_current_user_id(),
            worker=self._get_worker_id(form),
        )

    def _get_current_user_id(self) -> UUID:
        current_user = self.session.get_current_user()
        if current_user is None:
            raise ValueError("User is not logged in")
        return current_user

    def _get_worker_id(self, form: InviteWorkerToCompanyForm) -> UUID:
        try:
            return UUID(form.get_worker_id())
        except ValueError:
            raise ValueError("worker_id is not a valid UUID")
