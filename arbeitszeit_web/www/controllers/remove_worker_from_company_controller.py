from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.interactors.remove_worker_from_company import (
    Request as InteractorRequest,
)
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session, UserRole
from arbeitszeit_web.translator import Translator


@dataclass
class RemoveWorkerFromCompanyController:
    notifier: Notifier
    translator: Translator

    def create_interactor_request(
        self, *, web_request: Request, session: Session
    ) -> InteractorRequest | None:
        company = self._extract_company_from_session(session)
        worker = self._extract_worker_from_request(web_request)
        if worker is None:
            self.notifier.display_warning(
                self.translator.gettext("Worker ID in request is invalid or missing.")
            )
            return None
        return InteractorRequest(company=company, worker=worker)

    def _extract_company_from_session(self, session: Session) -> UUID:
        user_role = session.get_user_role()
        assert user_role is not None
        assert user_role == UserRole.company
        company = session.get_current_user()
        assert company
        return company

    def _extract_worker_from_request(self, web_request: Request) -> UUID | None:
        worker = web_request.get_form("worker")
        if worker is None:
            return None
        try:
            worker_uuid = UUID(worker)
        except ValueError:
            return None
        return worker_uuid
