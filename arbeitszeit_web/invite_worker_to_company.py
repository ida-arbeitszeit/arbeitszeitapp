from dataclasses import dataclass
from typing import List, Protocol
from uuid import UUID

from arbeitszeit.use_cases import InviteWorkerToCompanyUseCase
from arbeitszeit_web.translator import Translator

from .session import Session


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


@dataclass
class ViewModel:
    notifications: List[str]


@dataclass
class InviteWorkerToCompanyPresenter:
    translator: Translator

    def present(
        self, use_case_response: InviteWorkerToCompanyUseCase.Response
    ) -> ViewModel:
        if use_case_response.is_success:
            notifications = [
                self.translator.gettext("Worker has been invited successfully.")
            ]
        else:
            notifications = [self.translator.gettext("Worker could not be invited.")]
        return ViewModel(
            notifications=notifications,
        )
