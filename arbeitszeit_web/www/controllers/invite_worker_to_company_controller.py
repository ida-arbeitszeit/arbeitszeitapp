from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.interactors.invite_worker_to_company import (
    InviteWorkerToCompanyInteractor,
)
from arbeitszeit_web.forms import InviteWorkerToCompanyForm
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator


@dataclass
class InviteWorkerToCompanyController:
    @dataclass
    class FormError(Exception):
        form: InviteWorkerToCompanyForm

    session: Session
    translator: Translator

    def import_request_data(
        self,
        request: Request,
    ) -> InviteWorkerToCompanyInteractor.Request:
        worker_id = self._get_worker_id(request)
        return InviteWorkerToCompanyInteractor.Request(
            company=self._get_current_user_id(),
            worker=worker_id,
        )

    def _get_current_user_id(self) -> UUID:
        current_user = self.session.get_current_user()
        assert current_user
        return current_user

    def _get_worker_id(self, request: Request) -> UUID:
        worker_id = request.get_form("worker_id") or ""
        worker_id = worker_id.strip()
        try:
            return UUID(worker_id)
        except ValueError:
            raise self.FormError(
                form=InviteWorkerToCompanyForm(
                    worker_id_value=worker_id,
                    worker_id_errors=[self.translator.gettext("Invalid UUID")],
                )
            )
