from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases.delete_draft import DeleteDraftUseCase
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session


@dataclass
class DeleteDraftController:
    class Failure(Exception):
        pass

    session: Session

    def get_request(self, request: Request, draft: UUID) -> DeleteDraftUseCase.Request:
        referer = request.get_header("Referer")
        if referer is not None:
            self.session.set_next_url(referer)
        current_user = self.session.get_current_user()
        if current_user is None:
            raise self.Failure()
        return DeleteDraftUseCase.Request(
            deleter=current_user,
            draft=draft,
        )
